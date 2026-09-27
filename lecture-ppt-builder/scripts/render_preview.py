# -*- coding: utf-8 -*-
"""用本机 PowerPoint COM 把 pptx 逐页渲染为 PNG 预览（1920x1080）。

用法（Windows，需本机安装 PowerPoint 与 pywin32）：
    python render_preview.py <pptx绝对路径> <输出目录>

输出文件名为「幻灯片1.PNG … 幻灯片N.PNG」。
注意：Read 工具有图片缓存——渲染后复查同一页面时，
先把 PNG 复制成新文件名再读，否则看到的是旧图。
"""
import shutil
import sys
from pathlib import Path

import win32com.client

if len(sys.argv) < 3:
    sys.exit("usage: render_preview.py <pptx_abs_path> <out_dir>")

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

if not SRC.is_absolute() or not SRC.exists():
    sys.exit(f"pptx not found (must be absolute path): {SRC}")

if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

app = win32com.client.Dispatch("PowerPoint.Application")
try:
    pres = app.Presentations.Open(str(SRC), ReadOnly=True, WithWindow=False)
    pres.Export(str(DST), "PNG", 1920, 1080)
    pres.Close()
finally:
    app.Quit()
print("rendered:", DST, len({f.name.lower() for f in DST.iterdir() if f.suffix.lower() == ".png"}))
