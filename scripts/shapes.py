"""把一个或多个行政边界（bounds/*.json）合成底图轮廓，写进 geo-<名>.js 的 GEO.shape，
并把街道/水面等图层裁到轮廓附近（文件变小）。cfg 里写 shape:true 就按这个轮廓画底图。
用法：python3 shapes.py <geo名> <边界键1> [边界键2 ...] [--minus-sea] [--crop 西,南,东,北]
--minus-sea  减掉大片水域（海边城市的行政边界常常包含海面）
--crop       裁掉和行程无关的部分
例：  python3 shapes.py tri gdansk sopot gdynia --minus-sea --crop 18.35,54.27,18.80,54.63
注意：裁剪会改写 geo 文件；想换轮廓时先重跑 geo_tiles.py 再跑这个。"""
import json, sys
from shapely.geometry import shape, mapping, MultiPolygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

args = [a for a in sys.argv[1:]]
crop = None
if '--crop' in args:
    i = args.index('--crop'); crop = tuple(map(float, args[i + 1].split(','))); del args[i:i + 2]
sea = '--minus-sea' in args
args = [a for a in args if a != '--minus-sea']
name, keys = args[0], args[1:]
if not keys:
    sys.exit(__doc__)

f = f'geo-{name}.js'
G = json.loads(open(f).read()[len('window.GEO='):-1])
G.pop('shape', None)
shp = unary_union([shape(json.load(open(f'bounds/{k}.json'))).buffer(0) for k in keys])
if sea:
    big = [p for p in getattr(shape(G['water']['geometry']), 'geoms', []) if p.area > 0.002]
    if big:
        shp = shp.difference(unary_union(big).buffer(0.0005))
if crop:
    shp = shp.intersection(box(*crop))
if 'data_bbox' in G:   # 底图数据范围外没有街道，轮廓也不要超出
    shp = shp.intersection(box(*G['data_bbox']))
polys = [p for p in getattr(shp, 'geoms', [shp]) if p.geom_type == 'Polygon' and p.area > shp.area * 0.002]
shp = MultiPolygon([orient(p.simplify(0.00005), -1.0) for p in polys])
feat = lambda g: {'type': 'Feature', 'properties': {}, 'geometry': g}
G['shape'] = feat(mapping(shp))
near = shp.buffer(0.01)
for k, v in list(G.items()):
    if k in ('shape', 'towns', 'data_bbox') or not isinstance(v, dict):
        continue
    g = shape(v['geometry']).intersection(near)
    if g.is_empty:
        v['geometry'] = {'type': v['geometry']['type'], 'coordinates': []}
    elif 'Polygon' in v['geometry']['type']:
        v['geometry'] = mapping(MultiPolygon([orient(p, -1.0) for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon']))
    else:
        ls = [l for l in getattr(g, 'geoms', [g]) if l.geom_type == 'LineString']
        v['geometry'] = {'type': 'MultiLineString', 'coordinates': [[list(c) for c in l.coords] for l in ls]}
b = shp.bounds
G['shape_bounds'] = [[b[0], b[1]], [b[2], b[3]]]
open(f, 'w').write('window.GEO=' + json.dumps(G, ensure_ascii=False) + ';')
print(name, len(polys), 'parts, bounds', [round(x, 4) for x in b])
