#!/usr/bin/env python3
"""
render-a3.py — A3 报告 → HTML 渲染

用法：
    python render-a3.py <project-slug> [--output a3-report.html]

读取 <project_dir>/a3-report.md → 渲染成 A3 尺寸的 HTML，可打印贴墙。

项目路径：
    默认：E:\00-学习\00-张振华\projects\six-sigma\<slug>\
    覆盖：环境变量 SIX_SIGMA_PROJECTS_ROOT=<自定义路径>
"""
import argparse
import os
import sys
from pathlib import Path

# Windows PowerShell 默认 GBK，stdout reconfigure 为 utf-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_PROJECTS_ROOT = Path(r"E:\00-学习\00-张振华\projects")
PROJECTS_ROOT = Path(os.environ.get("SIX_SIGMA_PROJECTS_ROOT", str(DEFAULT_PROJECTS_ROOT))) / "six-sigma"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>A3 报告 — {title}</title>
<style>
  @page {{ size: A3 landscape; margin: 1cm; }}
  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    margin: 20px;
    background: #fafafa;
    color: #222;
    line-height: 1.5;
  }}
  .a3-container {{
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
  }}
  h1 {{
    text-align: center;
    color: #1976d2;
    border-bottom: 3px solid #1976d2;
    padding-bottom: 10px;
    margin-top: 0;
  }}
  h2 {{
    color: #1976d2;
    border-left: 5px solid #1976d2;
    padding-left: 10px;
    margin-top: 30px;
    background: #e3f2fd;
    padding: 8px 12px;
  }}
  h3 {{ color: #1565c0; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
  }}
  th, td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
  }}
  th {{
    background: #1976d2;
    color: white;
  }}
  tr:nth-child(even) {{ background: #f5f5f5; }}
  blockquote {{
    border-left: 4px solid #1976d2;
    padding-left: 12px;
    color: #555;
    background: #f5f5f5;
    padding: 8px 12px;
  }}
  .meta {{
    text-align: center;
    color: #888;
    font-size: 0.9em;
    margin-bottom: 20px;
  }}
  hr {{
    border: none;
    border-top: 1px dashed #ccc;
    margin: 20px 0;
  }}
  @media print {{
    body {{ background: white; }}
    .a3-container {{ box-shadow: none; padding: 10px; }}
  }}
</style>
</head>
<body>
<div class="a3-container">
{content}
</div>
</body>
</html>
"""


def md_to_html(md_text: str) -> str:
    """极简 Markdown → HTML 渲染（标题/表格/粗体/列表/blockquote/段落）"""
    import re
    lines = md_text.split("\n")
    html = []
    in_table = False
    in_list = False
    table_rows = []

    def flush_table():
        if not table_rows:
            return ""
        out = ["<table>"]
        if len(table_rows) > 0:
            out.append("<thead><tr>")
            for c in table_rows[0]:
                out.append(f"<th>{c.strip()}</th>")
            out.append("</tr></thead>")
            if len(table_rows) > 1:
                out.append("<tbody>")
                for row in table_rows[1:]:
                    out.append("<tr>")
                    for c in row:
                        out.append(f"<td>{c.strip()}</td>")
                    out.append("</tr>")
                out.append("</tbody>")
        out.append("</table>")
        table_rows.clear()
        return "\n".join(out)

    def parse_table_row(line):
        cells = [c for c in line.strip().strip("|").split("|")]
        return cells

    for line in lines:
        # Table
        if line.strip().startswith("|") and line.strip().endswith("|"):
            in_table = True
            cells = parse_table_row(line)
            # separator row |---|---|---|
            if all(set(c) <= set("-: ") for c in cells):
                continue
            table_rows.append(cells)
            continue
        else:
            if in_table:
                html.append(flush_table())
                in_table = False

        # Headings
        if line.startswith("# "):
            html.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith("## "):
            if in_list:
                html.append("</ul>"); in_list = False
            html.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            html.append(f"<h3>{line[4:].strip()}</h3>")
        # Blockquote
        elif line.startswith("> "):
            html.append(f"<blockquote>{line[2:].strip()}</blockquote>")
        # Checkbox
        elif line.strip().startswith("- ["):
            if not in_list:
                html.append("<ul>"); in_list = True
            checked = "[x]" in line
            text = line.replace("- [x]", "").replace("- [ ]", "").strip()
            mark = "✅" if checked else "☐"
            html.append(f"<li>{mark} {text}</li>")
        # Lists
        elif line.strip().startswith("- "):
            if not in_list:
                html.append("<ul>"); in_list = True
            html.append(f"<li>{line.strip()[2:]}</li>")
        # Empty
        elif not line.strip():
            if in_list:
                html.append("</ul>"); in_list = False
            html.append("")
        # Paragraph
        else:
            if in_list:
                html.append("</ul>"); in_list = False
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            html.append(f"<p>{text}</p>")

    if in_list:
        html.append("</ul>")
    if in_table:
        html.append(flush_table())

    return "\n".join(html)


def render(project_dir: Path, output: Path) -> Path:
    md_file = project_dir / "a3-report.md"
    if not md_file.exists():
        print(f"❌ 未找到 {md_file}", file=sys.stderr)
        sys.exit(1)
    md_text = md_file.read_text(encoding="utf-8")

    # title from first H1 or folder name
    title = project_dir.name
    for line in md_text.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    html_body = md_to_html(md_text)
    full_html = HTML_TEMPLATE.format(title=title, content=html_body)
    output.write_text(full_html, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="A3 报告 → HTML 渲染")
    parser.add_argument("slug", help="项目 slug")
    parser.add_argument("--output", "-o", help="输出 HTML 路径（默认 <project>/a3-report.html）")
    args = parser.parse_args()

    project_dir = PROJECTS_ROOT / args.slug
    if not project_dir.exists():
        print(f"❌ 项目目录不存在：{project_dir}", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else project_dir / "a3-report.html"
    out_path = render(project_dir, out)
    print(f"✅ A3 报告已渲染：{out_path}")
    print(f"   在浏览器打开 → Cmd+P → 选 A3 横向 → 打印")


if __name__ == "__main__":
    main()
