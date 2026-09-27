# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""把手稿 .docx 导出为带样式标记的纯文本，供核对手稿标题层级用。

用法（推荐 uv，依赖自动安装）：
    uv run export_manuscript.py <手稿.docx> [输出.txt]
    或：python export_manuscript.py <手稿.docx> [输出.txt]   # 需已装 python-docx

输出格式：
    [Heading 1] 一、忒拜王族的诅咒
    [Normal] 正文段落……
    [TABLE 3x2] 行1cell1 | 行1cell2
                行2cell1 | 行2cell2

特点：按文档流顺序输出段落与表格（python-docx 的 doc.paragraphs 会丢表格位置），
空段落跳过。不指定输出路径时写到系统临时目录并打印路径。
"""
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.document import Document as _Doc
from docx.oxml.ns import qn
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    """按文档流顺序产出 Paragraph / Table"""
    if isinstance(parent, _Doc):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError(type(parent))
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: export_manuscript.py <manuscript.docx> [out.txt]")
    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"not found: {src}")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else \
        Path(tempfile.gettempdir()) / (src.stem + "_exported.txt")

    doc = Document(str(src))
    lines = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            t = block.text.strip()
            if t:
                lines.append(f"[{block.style.name}] {t}")
        else:
            rows = block.rows
            ncol = len(block.columns)
            lines.append(f"[TABLE {len(rows)}x{ncol}]")
            for r in rows:
                cells = [" / ".join(p.text.strip() for p in c.paragraphs if p.text.strip())
                         for c in r.cells]
                lines.append("    " + " | ".join(cells))

    out.write_text("\n".join(lines), encoding="utf-8")
    n_chars = sum(len(l) for l in lines)
    print(f"exported: {out}  blocks={len(lines)} chars={n_chars}")


if __name__ == "__main__":
    main()
