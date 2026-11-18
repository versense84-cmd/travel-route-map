"""用 Nominatim（OSM 地名搜索，免 key）取行政边界轮廓，存到项目的 bounds/<键>.json
轮廓用来做"像国家地图一样"的底图形状（不用矩形框）。
用法：python3 bounds.py <键> "<搜索词>" [--pick N]
例：  python3 bounds.py brno_center "Město Brno"
      python3 bounds.py warsaw_srod "Śródmieście, Warszawa"
会列出前几个带边界的结果，默认取第 1 个；不对就加 --pick 2 换一个。"""
import json, sys, os, urllib.request, urllib.parse

key, q = sys.argv[1], sys.argv[2]
pick = int(sys.argv[sys.argv.index('--pick') + 1]) if '--pick' in sys.argv else 1
u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
    {'q': q, 'format': 'json', 'polygon_geojson': 1, 'limit': 8, 'polygon_threshold': 0.0001})
r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'travel-route-map/1.0'}), timeout=60))
r = [x for x in r if x.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon')]
if not r:
    sys.exit('没找到带边界的结果：换个写法（加上级行政区、用当地语言名）')
for i, x in enumerate(r, 1):
    print(('→ ' if i == pick else '  ') + f"{i}. {x['class']}/{x['type']} {x['display_name'][:70]} bbox={[round(float(b), 4) for b in x['boundingbox']]}")
os.makedirs('bounds', exist_ok=True)
json.dump(r[pick - 1]['geojson'], open(f'bounds/{key}.json', 'w'))
print('写入', os.path.abspath(f'bounds/{key}.json'))
