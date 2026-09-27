# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "python-pptx>=1.0",
#   "Pillow>=10",
#   "pywin32>=306; sys_platform == 'win32'",
# ]
# ///
"""环境自检 + 模板冒烟测试（跨平台支持 Windows 与 Linux）。

用法（推荐 uv，依赖自动安装）：
    uv run smoke_test.py            # 只自检依赖 + 构建冒烟 pptx（验证七种页型代码）
    uv run smoke_test.py --render   # 追加渲染验证（Windows 调用 COM，Linux 调用 LibreOffice+pdftoppm）

自包含：用 PIL 现场生成测试图，不依赖任何外部图片素材。
通过标准：
    1. 核心依赖检查全 PASS；
    2. 七种页型全部生成并成功保存 smoke.pptx；
    3. （若带 --render）逐页 PNG 导出成功且生成 7 张预览图。
"""
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "assets" / "ppt_template.py"
RENDERER = SKILL / "scripts" / "render_preview.py"

ok = True


def check(name, fn):
    global ok
    try:
        fn()
        print(f"  PASS  {name}")
    except Exception as e:
        ok = False
        print(f"  FAIL  {name}: {e}")


print("== 1. 依赖与环境检查 ==")
check("python-pptx", lambda: __import__("pptx"))
check("Pillow", lambda: __import__("PIL"))

sys_name = platform.system()
if sys_name == "Windows":
    check("pywin32 (PowerPoint COM)", lambda: __import__("win32com.client"))
else:
    # Linux / macOS 跨平台渲染引擎检查
    def check_linux_renderer():
        lo = shutil.which("libreoffice") or shutil.which("soffice")
        if not lo:
            raise FileNotFoundError("neither libreoffice nor soffice found in PATH")
        ppm = shutil.which("pdftoppm")
        if not ppm:
            raise FileNotFoundError("pdftoppm not found in PATH (install poppler-utils)")

    check(f"{sys_name} 渲染引擎 (libreoffice + pdftoppm)", check_linux_renderer)

print("== 2. 模板冒烟（七种页型构建） ==")
work = Path(tempfile.mkdtemp(prefix="lecskill_smoke_"))


def build_smoke():
    from PIL import Image, ImageDraw

    # 现场生成一张"油画感"测试图（暖色渐变 + 上部亮区模拟人物面部位置）
    img = Image.new("RGB", (1600, 1200))
    dr = ImageDraw.Draw(img)
    for y in range(1200):
        dr.line([(0, y), (1600, y)],
                fill=(90 + y // 30, 60 + y // 40, 40 + y // 50))
    dr.ellipse([650, 150, 950, 450], fill=(200, 170, 140))  # 面部亮区
    test_img = work / "test_painting.jpg"
    img.save(test_img, "JPEG", quality=90)

    tpl = TEMPLATE.read_text(encoding="utf-8")
    tpl = tpl.replace(
        'OUT = HERE / "出讲义" / "第X讲_标题.pptx"          # TODO 改成本讲文件名',
        'OUT = HERE / "smoke.pptx"')
    content = f'''
IMG["t"] = Path(r"{test_img}")
pg()
s_cover("冒烟测试", "七种页型自检", "smoke", IMG["t"], en="smoke test")
s_section("壹", "章节页", "满版画 + 大序号", IMG["t"])
s_quote("测试 · 引文 1–3", ["第一行引文。", "第二行引文。", "第三行引文。"],
        "—— 《测试篇》1–3", IMG["t"], note="注释行。")
s_dark("测试 · 设问", "深色思辨页", [("设问一：", "正文。"), "纯文本条目。"], pg())
_s, _tw = s_content("1.1 · 测试", "象牙图文页", pg(), lead="导语。", img=IMG["t"], img_cap="图注")
bullets(_s, M, 2.55, _tw, [("要点一：", "正文。")], size=16)
point_bar(_s, M, 6.0, _tw, "结论条。")
s_compare("2.1 · 测试", "双栏对照页", pg(),
          left=dict(head="左栏", sub="左副标", items=[("甲：", "乙")]),
          right=dict(head="右栏", sub="右副标", items=[("丙：", "丁")]), bottom="对照结论。")
s_cards("3.1 · 测试", "卡片页", pg(),
        [("a", "卡一", "正文"), ("b", "卡二", "正文"), ("c", "卡三", "正文")],
        cols=3, bottom="卡片结论。")
'''
    tpl = tpl.replace("prs.save(str(OUT))", content + "\nprs.save(str(OUT))")
    build = work / "build_smoke.py"
    build.write_text(tpl, encoding="utf-8")
    r = subprocess.run(_runner() + [str(build)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]
    assert (work / "smoke.pptx").exists(), "pptx not saved"
    print(f"        built: {work / 'smoke.pptx'}")


def _runner():
    """子进程启动器：有 uv 用 uv run（按 PEP 723 头自装依赖），否则当前解释器"""
    uv = shutil.which("uv")
    return [uv, "run"] if uv else [sys.executable]


check("build 7 page types", build_smoke)

if "--render" in sys.argv:
    engine_name = "PowerPoint COM" if sys_name == "Windows" else "LibreOffice + pdftoppm"
    print(f"== 3. 逐页预览渲染验证 ({engine_name}) ==")

    def do_render():
        r = subprocess.run(_runner() + [str(RENDERER),
                                        str(work / "smoke.pptx"), str(work / "preview")],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-400:]
        n = len(list((work / "preview").glob("*.PNG")))
        assert n == 7, f"expected 7 pages, got {n}"
        print(f"        rendered 7 pages -> {work / 'preview'}")

    check("render preview", do_render)

print()
print("SMOKE " + ("PASSED" if ok else "FAILED"), "| workdir:", work)
if not ok:
    sys.exit(1)
