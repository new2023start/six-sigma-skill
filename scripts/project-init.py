#!/usr/bin/env python3
"""
project-init.py — 6 Sigma 项目初始化脚本

用法：
    python project-init.py <project-slug> --title "降低注塑件不良率" --champion "张三" --bb "李四"

作用：
    1. 创建项目目录结构
    2. 初始化 state.json（单一可信源）
    3. 创建空的阶段目录 + README 占位
    4. 输出项目根路径
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Windows PowerShell 默认 GBK，stdout reconfigure 为 utf-8 才能正确输出 emoji / 中文
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 项目根目录：默认 E:\00-学习\00-张振华\projects\six-sigma\
# 可通过环境变量 SIX_SIGMA_PROJECTS_ROOT 覆盖（支持绝对路径）
DEFAULT_PROJECTS_ROOT = Path(r"E:\00-学习\00-张振华\projects")
PROJECTS_ROOT = Path(os.environ.get("SIX_SIGMA_PROJECTS_ROOT", str(DEFAULT_PROJECTS_ROOT))) / "six-sigma"


def slugify(s: str) -> str:
    """简单 slug：保留中文/英文/数字，用 '-' 替代空格"""
    return s.strip().replace(" ", "-").replace("/", "-")


def init_project(slug: str, title: str, champion: str = "", black_belt: str = "") -> Path:
    """初始化项目目录"""
    project_dir = PROJECTS_ROOT / slug
    if project_dir.exists():
        print(f"⚠️  项目目录已存在：{project_dir}", file=sys.stderr)
        return project_dir

    # 创建阶段目录
    for phase in ["define", "measure", "analyze", "improve", "control"]:
        (project_dir / phase).mkdir(parents=True, exist_ok=True)

    # state.json（单一可信源）
    state = {
        "project": {
            "slug": slug,
            "title": title,
            "champion": champion,
            "black_belt": black_belt,
            "created": datetime.now().isoformat(timespec="seconds"),
        },
        "phase": "define",
        "phase_history": [
            {"phase": "define", "entered": datetime.now().isoformat(timespec="seconds"), "status": "in_progress"}
        ],
        "tollgates": {
            "d_to_m": {"passed": False, "checked_at": None, "notes": ""},
            "m_to_a": {"passed": False, "checked_at": None, "notes": ""},
            "a_to_i": {"passed": False, "checked_at": None, "notes": ""},
            "i_to_c": {"passed": False, "checked_at": None, "notes": ""},
            "c_to_close": {"passed": False, "checked_at": None, "notes": ""},
        },
        "deliverables": {
            "define": {
                "charter": {"done": False, "path": "define/charter.md"},
                "sipoc": {"done": False, "path": "define/sipoc.md"},
                "voc_ctq": {"done": False, "path": "define/voc-ctq.md"},
                "project_plan": {"done": False, "path": "define/project-plan.md"},
            },
            "measure": {
                "data_collection_plan": {"done": False, "path": "measure/data-collection-plan.md"},
                "msa": {"done": False, "path": "measure/msa-plan.md"},
                "baseline_stats": {"done": False, "path": "measure/baseline-stats.md"},
            },
            "analyze": {
                "fishbone": {"done": False, "path": "analyze/fishbone.md"},
                "fmea": {"done": False, "path": "analyze/fmea.md"},
                "hypothesis_tests": {"done": False, "path": "analyze/hypothesis-tests.md"},
            },
            "improve": {
                "solution_matrix": {"done": False, "path": "improve/solution-matrix.md"},
                "pilot_plan": {"done": False, "path": "improve/pilot-plan.md"},
                "doe_results": {"done": False, "path": "improve/doe-results.md"},
            },
            "control": {
                "control_plan": {"done": False, "path": "control/control-plan.md"},
                "spc_charts": {"done": False, "path": "control/spc-charts.md"},
                "benefits_tracking": {"done": False, "path": "control/benefits-tracking.md"},
            },
        },
        "a3_report": {"done": False, "path": "a3-report.md"},
    }
    (project_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # README.md（人手可读）
    readme = f"""# {title}

| 项目 | 内容 |
|---|---|
| 项目编号 | {slug} |
| 主题 | {title} |
| Champion（项目倡导人） | {champion or "TBD"} |
| Black Belt（项目负责人） | {black_belt or "TBD"} |
| 创建时间 | {datetime.now().strftime("%Y-%m-%d")} |
| 当前阶段 | **D — Define** |
| 项目目录 | `{project_dir}` |

## 当前状态

参见 `state.json`。

## 下一步

进入 Define 阶段，按以下顺序完成核心交付物：

1. **项目章程**（charter）— 一页纸决策
2. **SIPOC** — 流程全景
3. **VOC/CTQ** — 客户声音 → 关键质量特性
4. **项目计划** — 时间表 + 里程碑

完成后跑 tollgate1（`references/tollgate-checklist.md`）→ 进入 M 阶段。
"""
    (project_dir / "README.md").write_text(readme, encoding="utf-8")

    return project_dir


def main():
    parser = argparse.ArgumentParser(description="初始化 6 Sigma 项目目录")
    parser.add_argument("slug", help="项目标识（kebab-case，建议用主题拼音或英文）")
    parser.add_argument("--title", required=True, help="项目主题")
    parser.add_argument("--champion", default="", help="项目 Champion")
    parser.add_argument("--bb", default="", help="Black Belt / 项目负责人")
    args = parser.parse_args()

    project_dir = init_project(args.slug, args.title, args.champion, args.bb)
    print(f"✅ 项目已创建：{project_dir}")
    print(f"   state.json: {project_dir / 'state.json'}")
    print(f"   README.md:  {project_dir / 'README.md'}")
    print()
    print("下一步：进入 Define 阶段，先做项目章程。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
