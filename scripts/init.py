"""建一个路线地图项目文件夹：拷入 engine.html / anim-template.html（项目里的 cfg、geo、routes 都放在这里）
用法：python3 init.py <项目文件夹>"""
import os, shutil, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dst = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
os.makedirs(os.path.join(dst, 'bounds'), exist_ok=True)
for f in ('engine.html', 'anim-template.html'):
    shutil.copy(os.path.join(SKILL, 'assets', f), dst)
print('项目文件夹就绪：', dst)
print('下一步：写 cfg-<名>.js（参考', os.path.join(SKILL, 'examples'), '），然后在这个文件夹里运行 build.py')
