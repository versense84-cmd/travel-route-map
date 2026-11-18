// 示例 1：航线图（上海虹桥 → 东京羽田）。不需要 geo/routes 数据，国界用 world-atlas。
// 出片：python3 <skill>/scripts/build.py flight 上海-东京 --still --render
//      要 4992x3328 之类的相机分辨率就加 --size 4992x3328（版面按 3:2 排，见 extent/fit 的注释）
window.CFG={
  countries:['China','Japan','South Korea','North Korea','Taiwan'],  // world-atlas 英文国名
  atlas:'50m',            // 海岸线精度：50m 更平滑（大范围用），10m 更细（单国用）
  lineWidth:5,fillOpacity:.5,
  fit:[[115.5,28.5],[143,28.5],[115.5,39.5],[143,39.5]],  // 画面要框住的经纬度范围（四个角）
  extent:[[40,90],[1430,1020]],                           // 地图放在画面哪块（右侧留给标题）；3:2 版面高 1280
  title:{over:'Flight',main:'Shanghai → Tokyo',zh:'上海虹桥 → 东京羽田',x:1655,y:220,size:60},
  legend:{x:1520,y:400,items:[['plane','飞机航线']]},
  stops:{
    sha:{en:'Shanghai Hongqiao',zh:'上海虹桥机场 SHA',p:[121.336,31.198],num:1,lx:-32,ly:12,a:'end',big:40},
    hnd:{en:'Tokyo Haneda',zh:'东京羽田机场 HND',p:[139.781,35.549],num:2,lx:-10,ly:62,a:'end',big:40},
  },
  seq:[
    {fade:'label',at:[126.2,31.9],en:'East China Sea',zh:'东 海',size:30,ls:6,zhLs:14,anchor:'middle'},
    {stop:'sha'},
    // planeIcon：画一架小飞机沿线飞（数值=飞机大小 px）；dur：这一段动画秒数；bend：弧度
    {leg:['sha','hnd'],mode:'plane',bend:-.2,dur:3.2,planeIcon:56,pill:['飞机','约 2 h 40 min','1,780 km'],at:{px:[820,300]},lead:'auto'},
    {stop:'hnd'},
  ],
};
