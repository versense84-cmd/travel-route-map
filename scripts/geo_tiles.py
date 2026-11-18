"""从 OpenFreeMap 矢量瓦片（OSM 数据，OpenMapTiles 结构，免 key）取底图，写成项目文件夹里的 geo-<名>.js
城市街道用 zoom 14，区域路网用 11–12。比 Overpass 快得多也稳得多。
用法：python3 geo_tiles.py <名> <南纬> <西经> <北纬> <东经> [zoom=14]
例：  python3 geo_tiles.py brno 49.180 16.585 49.210 16.632 14
产出图层：st_major / st_mid / st_minor（城市级才有）/ rail / river / water / park（城市级才有）/ towns"""
import json, math, sys, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
import mapbox_vector_tile
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

name = sys.argv[1]
S, Wb, N, E = map(float, sys.argv[2:6])
Z = int(sys.argv[6]) if len(sys.argv) > 6 else 14
UA = {'User-Agent': 'travel-route-map/1.0'}
TJ = json.load(urllib.request.urlopen(urllib.request.Request('https://tiles.openfreemap.org/planet', headers=UA), timeout=30))['tiles'][0]

def tile_xy(lat, lon, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)

def to_ll(x, y, z, px, py, ext):
    n = 2 ** z
    lon = (x + px / ext) / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + py / ext) / n))))
    return [round(lon, 5), round(lat, 5)]

def conv(g, f):
    t, c = g['type'], g['coordinates']
    if t == 'Point': return {'type': t, 'coordinates': f(*c)}
    if t in ('LineString', 'MultiPoint'): return {'type': t, 'coordinates': [f(*p) for p in c]}
    if t in ('MultiLineString', 'Polygon'): return {'type': t, 'coordinates': [[f(*p) for p in r] for r in c]}
    if t == 'MultiPolygon': return {'type': t, 'coordinates': [[[f(*p) for p in r] for r in pg] for pg in c]}

x0, y0 = tile_xy(N, Wb, Z); x1, y1 = tile_xy(S, E, Z)
tiles = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
if len(tiles) > 400:
    sys.exit(f'{len(tiles)} 块瓦片太多了：缩小范围或降低 zoom')

def fetch(t):
    x, y = t
    u = TJ.replace('{z}', str(Z)).replace('{x}', str(x)).replace('{y}', str(y))
    for _ in range(4):
        try: return t, urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        except Exception as e: err = e
    sys.exit(f'瓦片下载失败 {t} {err}')

with ThreadPoolExecutor(8) as ex:
    raw = list(ex.map(fetch, tiles))
print(name, len(tiles), 'tiles z', Z, flush=True)

L = {k: [] for k in ['st_major', 'st_mid', 'st_minor', 'rail', 'river']}
P = {'water': [], 'park': []}
towns = {}
MAJ = {'motorway', 'trunk', 'primary', 'secondary'} if Z >= 14 else {'motorway', 'trunk', 'primary'}
MID = {'tertiary'} if Z >= 14 else {'secondary', 'tertiary'}
for (x, y), data in raw:
    d = mapbox_vector_tile.decode(data, default_options={'y_coord_down': True})
    for lname, layer in d.items():
        ext = layer.get('extent', 4096)
        f = lambda px, py: to_ll(x, y, Z, px, py, ext)
        for ft in layer['features']:
            pr = ft['properties']; g = conv(ft['geometry'], f); gt = g['type']
            if lname == 'transportation' and 'Line' in gt:
                c = pr.get('class'); sub = pr.get('subclass')
                key = ('st_major' if c in MAJ else 'st_mid' if c in MID
                       else 'st_minor' if (Z >= 14 and (c == 'minor' or sub in ('pedestrian', 'living_street')))
                       else 'rail' if (c == 'rail' and pr.get('service') is None and sub == 'rail') else None)
                if key and pr.get('brunnel') != 'tunnel':
                    L[key] += [g['coordinates']] if gt == 'LineString' else g['coordinates']
            elif lname == 'waterway' and 'Line' in gt and pr.get('class') == 'river':
                L['river'] += [g['coordinates']] if gt == 'LineString' else g['coordinates']
            elif lname == 'water' and 'Polygon' in gt and pr.get('brunnel') != 'tunnel':
                P['water'].append(shape(g).buffer(0))
            elif (lname == 'park' or (lname == 'landcover' and pr.get('class') == 'wood')) and 'Polygon' in gt and Z >= 14:
                P['park'].append(shape(g).buffer(0))
            elif lname == 'place' and gt == 'Point' and pr.get('class') in ('city', 'town', 'village') and pr.get('name'):
                towns[pr['name']] = g['coordinates']

feat = lambda g: {'type': 'Feature', 'properties': {}, 'geometry': g}
GEO = {k: feat({'type': 'MultiLineString', 'coordinates': v}) for k, v in L.items()}
clip = box(Wb, S, E, N)
for k, v in P.items():
    u = unary_union(v).intersection(clip).simplify(0.00002) if v else None
    polys = [] if u is None or u.is_empty else ([u] if u.geom_type == 'Polygon' else [p for p in getattr(u, 'geoms', []) if p.geom_type == 'Polygon'])
    polys = [orient(p, -1.0) for p in polys if p.area > 1e-8]   # d3 球面：外环顺时针
    GEO[k] = feat({'type': 'MultiPolygon', 'coordinates': [mapping(p)['coordinates'] for p in polys]})
GEO['towns'] = [{'n': n, 'p': p} for n, p in towns.items()]
GEO['data_bbox'] = [Wb, S, E, N]
for k, v in GEO.items():
    if k != 'data_bbox':
        print(k, len(json.dumps(v)) // 1024, 'KB', flush=True)
open(f'geo-{name}.js', 'w').write('window.GEO=' + json.dumps(GEO, ensure_ascii=False) + ';')
print('写入', os.path.abspath(f'geo-{name}.js'))
