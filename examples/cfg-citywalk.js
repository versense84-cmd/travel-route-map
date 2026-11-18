// 示例 2：城市步行（捷克布尔诺老城）。底图 = 真实街道，形状 = 老城行政边界轮廓（不是矩形框）。
// 先在项目文件夹里准备数据：
//   python3 <skill>/scripts/geo_tiles.py brno 49.180 16.585 49.210 16.632 14   → geo-brno.js（街道/水/公园）
//   python3 <skill>/scripts/bounds.py brno_center "Město Brno"                  → bounds/brno_center.json（老城边界）
//   python3 <skill>/scripts/shapes.py brno brno_center                          → 轮廓写进 geo-brno.js
//   python3 <skill>/scripts/routes.py citywalk legs-citywalk.json               → routes-citywalk.js（步行路线+时间）
// 出片：python3 <skill>/scripts/build.py citywalk 布尔诺Day1 --still --render
window.CFG={
  geo:'brno',routes:'citywalk',countries:[],lineWidth:6,
  shape:true,extent:[[70,70],[1440,1010]],   // shape:true = 按 GEO.shape 轮廓铺底图，自动适配画面
  base:CITY_BASE,                            // 内置城市底图样式（公园/铁路/三级街道/水面）；区域图用 REGION_BASE
  title:{over:'Day 1',main:'Brno',zh:'布尔诺 · Citywalk',x:1655,y:220,size:80},
  legend:{x:1500,y:400,items:[['rail','火车'],['walk','步行']]},
  stops:{
    // p:[经度,纬度]；num 圆点里的编号；lx/ly 文字相对圆点的偏移；a 文字对齐 start/end/middle；small 小圆点
    bst:{en:'Brno hl. n.',zh:'火车站',p:[16.6129,49.1905],small:true,lx:30,ly:8,a:'start',big:32},
    brad:{en:'Old Town Hall',zh:'老市政厅 · Citywalk 出发',p:[16.6083,49.1932],num:1,lx:30,ly:-26,a:'start',big:36},
    bpet:{en:'Petrov Cathedral',zh:'彼得罗夫大教堂',p:[16.6073,49.1912],num:2,lx:32,ly:12,a:'start',big:36},
    bjak:{en:"St James' Church",zh:'圣雅各布教堂 · 看日落',p:[16.6080,49.1966],num:3,lx:32,ly:0,a:'start',big:36},
    bdin:{en:'Brewery Dinner',zh:'啤酒餐厅',p:[16.6059,49.1928],num:4,lx:-32,ly:-6,a:'end',big:36},
  },
  seq:[
    // 从画面外进场的线：起点写 {px:[x,y]} 像素坐标
    {train:[{px:[1400,1080]},'bst'],mode:'rail',bend:.1,pill:['火车','约 4 h','从布达佩斯'],at:{px:[1230,975]},lead:'auto'},
    {stop:'bst'},
    // route 引用 routes-citywalk.js 里的真实路线；pill = [方式, 时长, 距离]；at 胶囊位置，lead:'auto' 引线自动指回路线中点
    {leg:['bst','brad'],route:'bst_brad_foot',mode:'walk',pill:['步行','9 min','700 m'],at:{px:[1250,700]},lead:'auto'},
    {stop:'brad'},
    {leg:['brad','bpet'],route:'brad_bpet_foot',mode:'walk',pill:['步行','4 min','280 m'],at:{px:[640,810]},lead:'auto'},
    {stop:'bpet'},
    {leg:['bpet','bjak'],route:'bpet_bjak_foot',mode:'walk',pill:['步行','10 min','780 m'],at:{px:[1170,480]},lead:'auto'},
    {stop:'bjak'},
    // 不写 at 时胶囊自动摆在路线旁：side 哪一侧(1/-1)、pd 离线多远、pos 沿线位置(0–1)
    {leg:['bjak','bdin'],route:'bjak_bdin_foot',mode:'walk',pill:['步行','8 min','610 m'],side:1,pd:120},
    {stop:'bdin'},
  ],
};
