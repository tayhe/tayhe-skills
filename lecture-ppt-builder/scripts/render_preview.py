# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = ["pywin32>=306; sys_platform == 'win32'"]
# ///
"""用本机渲染引擎把 pptx 逐页渲染为 PNG 预览（1920x1080）。

用法（推荐 uv，依赖自动安装）：
    uv run render_preview.py <pptx绝对路径> <输出目录>
    或：python render_preview.py <pptx绝对路径> <输出目录>

支持平台：
    - Windows: 优先使用本机 PowerPoint COM (pywin32) 导出；
    - Linux: 自动调用 headless LibreOffice / soffice 转 PDF，再用 pdftoppm 渲染。

输出文件名为「幻灯片1.PNG … 幻灯片N.PNG」。
注意：Read 工具有图片缓存——渲染后复查同一页面时，
先把 PNG 复制成新文件名再读，否则看到的是旧图。
"""
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def render_preview(src_path: Path, dst_dir: Path):
    if not src_path.is_absolute() or not src_path.exists():
        sys.exit(f"pptx not found (must be absolute path): {src_path}")

    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)

    # Windows PowerPoint COM
    if platform.system() == "Windows":
        try:
            import win32com.client
            app = win32com.client.Dispatch("PowerPoint.Application")
            try:
                pres = app.Presentations.Open(str(src_path), ReadOnly=True, WithWindow=False)
                pres.Export(str(dst_dir), "PNG", 1920, 1080)
                pres.Close()
            finally:
                app.Quit()
            return
        except Exception as e:
            print(f"PowerPoint COM failed ({e}), falling back to LibreOffice/pdftoppm...")

    # Linux or Fallback: LibreOffice + pdftoppm
    lo_cmd = shutil.which("libreoffice") or shutil.which("soffice")
    if not lo_cmd:
        sys.exit("Error: Neither PowerPoint COM nor LibreOffice (libreoffice/soffice) found for rendering.")

    with tempfile.TemporaryDirectory(prefix="ppt_render_") as tmpdir:
        tmp = Path(tmpdir)
        cmd_lo = [lo_cmd, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(src_path)]
        res = subprocess.run(cmd_lo, capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit(f"LibreOffice conversion failed: {res.stderr or res.stdout}")

        pdf_path = tmp / (src_path.stem + ".pdf")
        if not pdf_path.exists():
            sys.exit(f"Expected PDF not found at {pdf_path}")

        ppm_cmd = shutil.which("pdftoppm")
        if not ppm_cmd:
            sys.exit("Error: pdftoppm not found. Please install poppler-utils.")

        cmd_ppm = [
            ppm_cmd, "-png", "-r", "144",
            "-scale-to-x", "1920", "-scale-to-y", "1080",
            str(pdf_path), str(tmp / "slide")
        ]
        res_ppm = subprocess.run(cmd_ppm, capture_output=True, text=True)
        if res_ppm.returncode != 0:
            sys.exit(f"pdftoppm conversion failed: {res_ppm.stderr or res_ppm.stdout}")

        png_files = sorted(tmp.glob("slide-*.png"))
        for i, png in enumerate(png_files, start=1):
            target = dst_dir / f"幻灯片{i}.PNG"
            shutil.copy2(png, target)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: render_preview.py <pptx_abs_path> <out_dir>")
    SRC = Path(sys.argv[1])
    DST = Path(sys.argv[2])
    render_preview(SRC, DST)
    rendered_count = len({f.name.lower() for f in DST.iterdir() if f.suffix.lower() == ".png"})
    print("rendered:", DST, rendered_count)
