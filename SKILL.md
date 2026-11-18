---
name: travel-route-map
description: 把旅行行程做成"复古地图风"的透明通道路线动画（ProRes 4444 带 alpha 的 MOV，可直接叠在 vlog 画面上）：国家/城市真实轮廓做底、粗白描边、斜体衬线地名、虚线路线逐段画出、每段标注交通方式+时长+距离，飞机航线还有小飞机沿虚线飞。触发：「做路线地图」「行程地图动画」「透明通道地图」「航线图」「vlog 地图」「从 A 飞到 B 的地图」「把这个行程做成地图」「标出每段多久」。支持城市步行（真实街道底图）、区域自驾、国家间火车/飞机，任意分辨率（如相机的 4992x3328）。
---

# 旅行路线地图（透明通道动画）

把一段行程做成可叠加在视频画面上的地图动画。风格：半透明暖褐色国土/城区 + 粗白描边 + IM Fell English 斜体地名 + 思源宋体中文 + 白色虚线路线 + 深褐色"时长胶囊"。

产物（每张图一个文件夹）：
- `<名>路线-透明通道-N秒.mov`：ProRes 4444 带透明通道，剪辑软件直接叠在画面上
- `<名>路线地图-透明.png`：最终画面的透明静态图
- `预览-<名>路线叠底.mp4`：叠在背景上的预览
- `动画工程/`：HyperFrames 工程，可再改

## 环境（第一次用先检查）

```bash
python3 -c "import mapbox_vector_tile, shapely" || pip3 install --user mapbox-vector-tile shapely
which ffmpeg node npx          # 没有就 brew install ffmpeg node
ls "/Applications/Google Chrome.app"   # 需要 Chrome 或 Chromium
```
渲染用 `npx -y hyperframes`（第一次会自动下载）。网络要能访问 cdn.jsdelivr.net、fonts.googleapis.com、tiles.openfreemap.org、nominatim.openstreetmap.org、routing.openstreetmap.de。

## 流程

`<skill>` 指本 skill 所在文件夹。所有命令在**项目文件夹**里运行。

1. **建项目**：`python3 <skill>/scripts/init.py ~/Downloads/<项目名>`，然后 `cd` 进去。
2. **先分析行程，再画**：把文案/行程拆成「每天 → 地点 → 交通方式 → 用时」。一张图一天（或一段），一张图最多 5–6 个编号点，太多就拆。
   - 有用户拍的照片/视频时，**用 GPS 核实真实地点和时间**，不要只信文案：
     `exiftool -n -T -DateTimeOriginal -GPSLatitude -GPSLongitude -FileName -r <照片文件夹>`（视频用 `-CreationDate`），按时间排序聚类，再用 Nominatim 反查地名。时间差就是每段真实用时，交通方式可以从速度和沿途点判断（例：机坪照片 → 其实坐了飞机）。
   - 文案和 GPS 冲突时照实画，并在回复里告诉用户。
3. **选底图**（见下方"底图怎么选"），准备数据：
   - 街道/路网：`python3 <skill>/scripts/geo_tiles.py <名> <南> <西> <北> <东> [zoom]`（城市 14，区域 11–12，范围要比轮廓大一圈）
   - 轮廓：`python3 <skill>/scripts/bounds.py <键> "<地名>"` → `python3 <skill>/scripts/shapes.py <名> <键…> [--minus-sea] [--crop 西,南,东,北]`
   - 真实路线 + 时长：写 `legs.json` → `python3 <skill>/scripts/routes.py <名> legs.json`
4. **写配置** `cfg-<名>.js`：从 `<skill>/examples/` 复制最接近的一个改（航线 → `cfg-flight.js`，城市/区域 → `cfg-citywalk.js`）。字段说明见下方。
5. **出静态图检查排版**：`python3 <skill>/scripts/build.py <cfg名> <输出名> --still`，把 PNG 叠到一张照片上看（文字有没有压线、胶囊有没有重叠、地名有没有出界），调 `lx/ly/at` 再出，直到干净。
6. **渲染**：`python3 <skill>/scripts/build.py <cfg名> <输出名> --render [--size 4992x3328] [--bg 背景.jpg]`。每条 1080p 约 2–4 分钟，4992x3328 更久，放后台跑。用 `ffprobe` 确认 `yuva444p12le` 和帧数。
7. 交付时列出每段时间的**来源**（GPS 实测 / 路线规划估算 / 航班常见时长）和需要用户确认的地方。

## 设计规则（用户反复确认过的偏好）

- **不要矩形底框**：底图必须是真实地理轮廓（国家、州、城市、城区），像国家地图一样；矩形会挡住整个画面。城区太挤时用**圆形放大镜**（`inset.circle:true`），也不要方框。
- **每一段都要标时长**：`pill:['步行','8 min','580 m']`，胶囊用引线指回路线；估算的写"约"。
- **城市段要有真实街道**（`geo_tiles` zoom 14），不能只画一条河。
- **画面要干净**：一张图最多 5–6 个编号点；同一条路往返只标一个胶囊（"往返各约 10 min"）；城市里打车的短途可以用平滑弧线代替弯弯绕绕的真实路线。
- 右侧留给标题（`title`）和图例（`legend`），地图放左侧 `extent`。
- 地名用当地真名（英文斜体）+ 中文说明一行。

## 底图怎么选

| 场景 | 做法 |
|---|---|
| 跨国 / 航线 | `countries:[...]` 用 world-atlas 国界，`fit` 框住范围，`atlas:'50m'` 海岸线更平滑 |
| 一个国家里的几天 | `countries:['Czechia']` + `rivers`/路网 |
| 一个州/区域自驾 | `geo_tiles` zoom 11–12 + 州的边界做 `shape`，`base:REGION_BASE` |
| 城市步行 | `geo_tiles` zoom 14 + 城区/老城边界做 `shape`，`base:CITY_BASE` |
| 海边城市 | `shapes.py --minus-sea` 去掉行政边界里的海面 |

## cfg 字段速查

```js
window.CFG={
  geo:'brno', routes:'citywalk',        // 读 geo-brno.js / routes-citywalk.js（可省）
  countries:['Japan'], atlas:'10m',     // world-atlas 国界（可空数组）
  shape:true,                           // 用 GEO.shape 轮廓做底（城市/区域）
  fit:[[lon,lat],…4个角], extent:[[x0,y0],[x1,y1]],   // 框住的经纬度 → 放到画面哪块（shape:true 时可省 fit）
  base:CITY_BASE | REGION_BASE,         // 内置底图样式，也可自己写 [{key,stroke,w,op,fill}]
  labels:[{text,at:[lon,lat],size,rot,op}],          // 轮廓内的地理标注（河名等）
  towns:['Opava'],                      // 显示 geo 里的城镇名
  title:{over,main,zh,x,y,size}, legend:{x,y,items:[[mode,'说明']]},
  inset:{rect:[x,y,w,h],circle:true,fit:[…],box:[[西,北],[东,南]],base:CITY_BASE,bg}, // 圆形放大镜
  stops:{ id:{en,zh,zh2,day,p:[lon,lat],num,small,inset,lx,ly,a,big,zhSize} },
  seq:[                                 // 按顺序出现
    {stop:'id'},
    {leg:[from,to], mode, route|via|bend|c1/c2, offset, pill:[方式,时长,距离], at:{px:[x,y]}|side/pd/pos, lead:'auto', dur, planeIcon, inset},
    {train:[from,to], ...},             // 同 leg，默认实线火车
    {fade:'label', at, en, zh, size, anchor},   // 文字淡入
    {fade:'inset'},                     // 放大镜出现
  ],
};
```
- 位置写法：站点 id / `[经度,纬度]` / `{px:[x,y]}`（画面像素，1920 宽版面）。
- `mode`：`walk` 点线、`car` 长虚线、`rail` 细实线、`bus` 点划线、`plane` 航线虚线、`cruise` 船、`metro` 粗实线。
- `planeIcon:56` 小飞机沿线飞，机头朝前；`dur:3.2` 这段动画放慢。
- 时间规则：开场 2.8 s，每段线 1.2 s（火车 1.5 s），每个点 0.55 s，结尾停 2.5 s。

## 常见坑

- **Overpass API 经常 502/超时**：底图一律用 `geo_tiles.py`（OpenFreeMap 矢量瓦片），几秒出。
- **静态图偶发丢字**（字体没加载完）：build.py 已截 4 次取最大文件。
- **render 偶发静默失败**（没有 MOV）：build.py 会重试一次；还不行就进 `动画工程/` 手动 `npx hyperframes render --format mov`。
- **轮廓外飘着字**：`labels` 只该放轮廓内；海上的字用 `fade:'label'`，或干脆不放。
- **轮廓里有一块海**：`shapes.py --minus-sea`；改轮廓前先重跑 `geo_tiles.py`（shapes 会裁剪 geo 文件）。
- **非 16:9 分辨率**：`--size 宽x高`，版面宽 1920、高按比例（3:2 → 1280），`extent`/标题 y 要按新高度重排。
- Nominatim 每秒最多 1 次请求，批量取边界时中间 sleep 1 s。
