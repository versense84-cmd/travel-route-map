"""在项目文件夹里用 engine.html + cfg-<名>.js 出片：透明静态 PNG、HyperFrames 动画工程、ProRes 4444 透明 MOV、叠底预览 MP4。
在项目文件夹里运行（init.py 建好的那个）：
  python3 <skill>/scripts/build.py <cfg名> <输出名> [--still] [--render] [--bg 背景图.jpg] [--size 4992x3328]
--still   出透明 PNG 静态图（先看排版用）
--render  出透明 MOV + 叠底预览 MP4
--size    输出分辨率，默认 1920x1080；版面宽固定 1920，高按比例（如 3:2 → 1920x1280），SVG 矢量放大，不糊
--bg      预览用的背景图；不给就用灰色渐变（只是预览，正片是透明 MOV）"""
import re, subprocess, sys, os, shutil

HERE = os.getcwd()
CHROME_CANDIDATES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                     '/Applications/Chromium.app/Contents/MacOS/Chromium',
                     shutil.which('google-chrome') or '', shutil.which('chromium') or '', shutil.which('chrome') or '']
CHROME = next((c for c in CHROME_CANDIDATES if c and os.path.exists(c)), None)
if not CHROME:
    sys.exit('找不到 Google Chrome / Chromium，请先安装')
if not os.path.exists(os.path.join(HERE, 'engine.html')):
    sys.exit('当前文件夹没有 engine.html：先运行 python3 <skill>/scripts/init.py <项目文件夹>，再 cd 进去')

name, zh = sys.argv[1], sys.argv[2]
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
bg = arg('--bg')
OW, OH = map(int, arg('--size', '1920x1080').split('x'))
LH = round(1920 * OH / OW)
out = os.path.join(HERE, zh)
os.makedirs(os.path.join(out, '动画工程'), exist_ok=True)
url = f'file://{HERE}/engine.html?cfg={name}&h={LH}'

def chrome(*args):
    return subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size=1920,{LH}',
                           '--virtual-time-budget=60000', '--allow-file-access-from-files', *args, url],
                          capture_output=True, text=True).stdout

# 1. 拿最终 SVG（偶发字体/数据没加载出来就重试）
for _ in range(4):
    dom = chrome('--dump-dom')
    m = re.search(r'<svg id="m".*?</svg>', dom, re.S)
    if m and 'data-total' in m.group(0):
        break
else:
    sys.exit('engine 没渲染出来：用浏览器打开 engine.html?cfg=' + name + ' 看控制台报错')
svg = m.group(0)
total = float(re.search(r'data-total="([\d.]+)"', svg).group(1))
dur = int(total + 0.999)
print(name, 'seq:', svg.count('class="seq'), 'duration', dur)

# 2. 透明静态图（偶发字体没加载完、文字丢失，文件会明显偏小：截几次留最大）
if '--still' in sys.argv:
    png = os.path.join(out, f'{zh}路线地图-透明.png')
    best = 0
    for i in range(4):
        tmp = png + f'.{i}.png'
        chrome('--default-background-color=00000000', f'--screenshot={tmp}')
        size = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        if size > best:
            best = size
            os.replace(tmp, png)
        elif size:
            os.remove(tmp)
    print('still', png)

# 3. 动画工程
tpl = open(os.path.join(HERE, 'anim-template.html')).read()
if (OW, OH) != (1920, 1080):
    svg = svg.replace(f'width="1920" height="{LH}"', f'width="{OW}" height="{OH}" viewBox="0 0 1920 {LH}"', 1)
    tpl = (tpl.replace('1920px', f'{OW}px').replace('1080px', f'{OH}px')
              .replace('data-width="1920" data-height="1080"', f'data-width="{OW}" data-height="{OH}"')
              .replace('width=1920, height=1080', f'width={OW}, height={OH}'))
html = tpl.replace('__TITLE__', f'{zh}路线透明叠加').replace('__DUR__', str(dur)).replace('__SVG__', svg)
open(os.path.join(out, '动画工程', 'index.html'), 'w').write(html)

# 4. 透明 MOV + 叠底预览
if '--render' in sys.argv:
    proj = os.path.join(out, '动画工程')
    mov = os.path.join(out, f'{zh}路线-透明通道-{dur}秒.mov')
    for attempt in range(2):   # render 偶发静默失败（没有 MOV），重试一次
        r = subprocess.run(['npx', '-y', 'hyperframes', 'render', '--format', 'mov', '--fps', '30', '-o', mov, '--quiet'],
                           cwd=proj, capture_output=True, text=True)
        if os.path.exists(mov):
            break
    else:
        sys.exit('hyperframes render 失败：\n' + r.stdout[-2000:] + r.stderr[-2000:])
    prev = os.path.join(out, f'预览-{zh}路线叠底.mp4')
    src = (['-loop', '1', '-i', bg] if bg else ['-f', 'lavfi', '-i', f'gradients=s={OW}x{OH}:c0=0x8a8f94:c1=0x3b3f44:speed=0'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *src, '-i', mov, '-filter_complex',
                    f'[0]scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH}[b];[b][1]overlay=shortest=1,format=yuv420p',
                    '-c:v', 'libx264', '-crf', '18', prev], check=True)
    print('rendered', mov)
