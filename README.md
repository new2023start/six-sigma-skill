# Six Sigma DMAIC Skill for OpenClaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-green.svg)](https://github.com/openclaw/openclaw)

按 **DMAIC**（Define / Measure / Analyze / Improve / Control）流程驱动 6 Sigma 项目从立项到结项全周期的 OpenClaw skill。覆盖项目章程、SIPOC、VOC/CTQ、MSA、假设检验、FMEA、控制计划、A3 报告。统计计算（Cp/Cpk、t 检验、ANOVA、正态性、DOE、Pareto）由 Python 脚本完成。

## ✨ 特性

- 🎯 **端到端流程**：5 阶段 × 14 个交付物模板，全流程覆盖
- 📊 **内置统计**：Cp/Cpk、t 检验、ANOVA、正态性、MSA、DOE、Pareto（基于 numpy + scipy + pandas）
- 📝 **Markdown 优先**：所有交付物是 `.md` 文件，可用 Obsidian / VSCode 直接编辑
- 🖨️ **A3 报告 → HTML**：一键渲染 A3 纸尺寸可打印报告
- 🔄 **状态机管理**：每个项目有 `state.json` 单一可信源
- 🇨🇳 **中文触发词**：原生支持中文 prompt（6 Sigma / DMAIC / 鱼骨图 / FMEA / Cp Cpk 等）

## 📦 安装

将本 skill 复制到 OpenClaw workspace 的 skills 目录：

```bash
# Linux / macOS
cp -r six-sigma ~/.openclaw/workspace/skills/

# Windows (PowerShell)
Copy-Item -Recurse six-sigma $env:USERPROFILE\.openclaw\workspace\skills\
```

安装 Python 依赖：

```bash
pip install numpy scipy pandas
```

## 🚀 快速开始

直接对 OpenClaw 说：

```
开始一个 6 Sigma 项目，主题是降低注塑件不良率
```

skill 会引导你完成立项 → 章程 → SIPOC → VOC/CTQ → 项目计划 → Tollgate 1 → 进入 M 阶段。

或者直接用 CLI：

```bash
# 新建项目
python scripts/project-init.py my-project --title "降低注塑件不良率" --champion "张总" --bb "李工"

# 计算 Cp/Cpk
python scripts/stats.py capability --data baseline.csv --lsl 24 --usl 26

# 跑 t 检验
python scripts/stats.py ttest --data before.csv --data2 after.csv --mode two

# 渲染 A3 报告
python scripts/render-a3.py my-project
```

## 📚 DMAIC 五阶段

| 阶段 | 核心交付物 | 常用工具 |
|---|---|---|
| **D**efine | charter, SIPOC, VOC/CTQ, plan | 头脑风暴、Kano、亲和图 |
| **M**easure | DCP, MSA, baseline | Cp/Cpk, GR&R, 正态性、控制图 |
| **A**nalyze | fishbone, 5Why, FMEA, hypothesis | t 检验、ANOVA、Pareto、回归 |
| **I**mprove | solution-matrix, pilot | DOE、配对 t 检验、防错 |
| **C**ontrol | control-plan, A3 | SPC、反应计划、收益追踪 |

## 🛠️ 统计脚本（`scripts/stats.py`）

提供 8 个核心功能（Python 模块 + CLI 双用）：

```bash
# 1. 描述统计
python scripts/stats.py describe --data baseline.csv

# 2. 过程能力（Cp/Cpk/Pp/Ppk）
python scripts/stats.py capability --data baseline.csv --lsl 24 --usl 26

# 3. t 检验（one / two / paired）
python scripts/stats.py ttest --data before.csv --data2 after.csv --mode two

# 4. 单因素 ANOVA
python scripts/stats.py anova --data trial.csv --value-col yield --group-col formula

# 5. 正态性（Shapiro-Wilk + Anderson-Darling）
python scripts/stats.py normality --data baseline.csv

# 6. 样本量计算
python scripts/stats.py sample-size --mode mean --delta 0.5 --sigma 1.0

# 7. Pareto 分析（80/20）
python scripts/stats.py pareto --data defects.csv --col defect_type

# 8. MSA / GR&R
python scripts/stats.py msa --data msa.csv --part-col part --operator-col op --value-col score
```

也可以作为 Python 模块导入：

```python
from scripts.stats import capability, t_test_two, normality_test

result = capability(data=[25.1, 24.8, 25.3, ...], lsl=24.0, usl=26.0)
print(result.cp, result.cpk, result.summary)
```

## 📁 目录结构

```
six-sigma/
├── SKILL.md                       # 入口 + 中文触发词 + 状态机
├── README.md                      # 本文件（GitHub）
├── LICENSE                        # MIT 协议
├── references/
│   ├── dmaic-playbook.md          # DMAIC 五阶段指南
│   ├── tool-catalog.md            # 工具选择表
│   └── tollgate-checklist.md      # 阶段门 review 检查
├── templates/                     # 14 个交付物模板
│   ├── charter.md                 # 项目章程
│   ├── sipoc.md                   # SIPOC 图
│   ├── voc-ctq.md                 # VOC → CTQ 树
│   ├── project-plan.md            # 项目计划
│   ├── data-collection-plan.md    # 数据收集计划
│   ├── msa-plan.md                # MSA 计划
│   ├── fishbone.md                # 鱼骨图
│   ├── 5why.md                    # 5 Why 分析
│   ├── fmea.md                    # 失效模式分析
│   ├── hypothesis-test-plan.md    # 假设检验
│   ├── solution-matrix.md         # 方案选择矩阵
│   ├── pilot-plan.md              # 试点计划
│   ├── control-plan.md            # 控制计划
│   └── a3-report.md               # A3 总结报告
└── scripts/
    ├── project-init.py            # 项目脚手架
    ├── stats.py                   # 统计核心（numpy/scipy/pandas）
    └── render-a3.py               # A3 → HTML 渲染
```

## 🔧 项目目录约定

每个 6 Sigma 项目独立目录，结构：

```
projects/six-sigma/<project-slug>/
├── state.json                     # 单一可信源（阶段进度）
├── README.md                      # 项目概览
├── define/                        # D 阶段交付物
├── measure/                       # M 阶段
│   ├── baseline-data.csv
│   └── stats-output.json
├── analyze/                       # A 阶段
├── improve/                       # I 阶段
├── control/                       # C 阶段
└── a3-report.md + a3-report.html  # 总结
```

**默认位置**：`E:\00-学习\00-张振华\projects\six-sigma\<slug>\`  
**可覆盖**：环境变量 `SIX_SIGMA_PROJECTS_ROOT=<自定义路径>`

## 📊 与 OpenClaw 其他 skill 的关系

- **依赖 numpy / scipy / pandas** — 一次性 `pip install`
- **不连外部系统**（MES / SPC）— 数据手动导入 CSV
- **不做团队协作**（无审批流 / 多人编辑）

## 🤝 贡献

欢迎贡献：
- 行业特定模板（医疗 / 金融 / IT 服务的 6 Sigma 实施差异）
- 统计函数扩展（非参数检验 / 时间序列 / DOE 进阶）
- 触发词本地化（英文 / 日文）
- 文档优化

提 PR 前请确保：
1. 跑过 demo 流程的 end-to-end 测试
2. 不破坏向后兼容
3. 更新 `SKILL.md` 中的触发词（如新增）

## 📝 License

[MIT](LICENSE) © 2026 Daniel.zhang

## 🙏 致谢

- DMAIC 方法论参考：George et al., *The Lean Six Sigma Pocket Toolbook* (McGraw-Hill)
- ASQ Certified Six Sigma Black Belt Body of Knowledge
- scipy / numpy / pandas 维护者
- OpenClaw 团队
