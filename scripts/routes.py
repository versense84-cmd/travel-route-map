"""查真实路线（FOSSGIS OSRM 公共服务，免 key）：几何 + 距离 + 时间，写成 routes-<名>.js
用法：python3 routes.py <名> <legs.json>
legs.json 格式：
  {"points": {"station": [16.6129, 49.1905], "townhall": [16.6083, 49.1932]},
   "legs":   [["station", "townhall", "foot"], ["townhall", "castle", "car"]]}
方式：foot（步行）/ car（开车）/ bike（骑行）。坐标是 [经度, 纬度]。
cfg 里用 route:'station_townhall_foot' 引用；打印出的分钟数是不含停留的估算。"""
import json, sys, time, urllib.request

name, spec = sys.argv[1], json.load(open(sys.argv[2]))
P, R = spec['points'], {}
SVC = {'car': ('routed-car', 'driving'), 'foot': ('routed-foot', 'foot'), 'bike': ('routed-bike', 'bike')}
for a, b, m in spec['legs']:
    sv, pr = SVC[m]
    c = f'{P[a][0]},{P[a][1]};{P[b][0]},{P[b][1]}'
    u = f'https://routing.openstreetmap.de/{sv}/route/v1/{pr}/{c}?overview=full&geometries=geojson'
    for t in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'travel-route-map/1.0'}), timeout=40))['routes'][0]
            break
        except Exception as e:
            print('retry', a, b, e); time.sleep(4)
    else:
        sys.exit(f'{a}→{b} 查不到路线')
    k = f'{a}_{b}_{m}'
    R[k] = {'g': [[round(x, 5), round(y, 5)] for x, y in r['geometry']['coordinates']],
            'km': round(r['distance'] / 1000, 2), 'min': round(r['duration'] / 60, 1)}
    print(f"{k}: {R[k]['km']} km, {R[k]['min']} min")
open(f'routes-{name}.js', 'w').write('window.ROUTES=' + json.dumps(R) + ';')
