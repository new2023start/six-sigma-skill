---
name: six-sigma
description: 6 Sigma 项目辅助工具，按 DMAIC（Define/Measure/Analyze/Improve/Control）流程驱动项目立项到结项全周期。覆盖项目章程、SIPOC、VOC/CTQ、数据收集计划、MSA、鱼骨图、5 Why、假设检验、FMEA、试点、控制计划、A3 报告；统计计算（Cp/Cpk、t 检验、ANOVA、正态性、DOE、Pareto）由 Python 脚本完成；模板驱动对话式填充，最终产出 Markdown 项目文档。触发:6 sigma, 六西格玛, 六西格玛项目, DMAIC, 定义阶段, 测量阶段, 分析阶段, 改进阶段, 控制阶段, 鱼骨图, fishbone, FMEA, Cp Cpk, 过程能力, 项目章程, SIPOC, VOC, CTQ, 黑带, 绿带, 质量改进, 过程改进, 持续改进, 数据收集计划, MSA, DOE, A3 报告, 控制计划, 试点。
license: MIT
version: 1.0.0
author: gateway-owner
created: 2026-10-06
---

# Six Sigma Skill

## 这是什么

一个按 **DMAIC** 流程驱动 6 Sigma 项目从立项到结项全过程的辅助 skill。对话式引导 → 模板自动填充 → 阶段门（tollgate）review → 最终 A3 报告。

## 五阶段覆盖

| 阶段 | 核心交付物 | 触发词 |
|---|---|---|
| **D**efine（定义） | 项目章程、SIPOC、VOC/CTQ、项目计划 | "新建项目"/"项目章程"/"SIPOC"/"VOC" |
| **M**easure（测量） | 数据收集计划、MSA、过程基线、Cp/Cpk | "数据收集计划"/"做 MSA"/"算 Cp/Cpk" |
| **A**nalyze（分析） | 鱼骨图、5 Why、假设检验、FMEA、Pareto | "画鱼骨图"/"5 Why"/"跑 t 检验"/"FMEA" |
| **I**mprove（改进） | 方案生成、选择矩阵、试点、DOE | "选方案"/"试点计划"/"DOE" |
| **C**ontrol（控制） | 控制计划、SPC、收益追踪、结项 | "控制计划"/"SPC"/"结项"/"A3 报告" |

## 快速开始

直接说（任选其一）：

- "开始一个 6 Sigma 项目，主题是 XXX"
- "新建项目 XXX"
- "进入 Measure 阶段"
- "计算 Cp/Cpk"
- "生成鱼骨图"
- "渲染 A3 报告"
- "项目状态"（查进度）

skill 会：
1. **引导提问**：按阶段需要的关键问题（每阶段 5-10 个）
2. **填充模板**：自动把答案写入对应模板
3. **保存项目**：写入 `E:\00-学习\00-张振华\projects\six-sigma\<slug>\`（可设 `SIX_SIGMA_PROJECTS_ROOT` 环境变量覆盖）
4. **更新状态**：写 `state.json`（阶段进度、已完成交付物）
5. **阶段门检查**：每次进入下一阶段前跑 tollgate checklist

## 项目目录结构

```
E:\00-学习\00-张振华\projects\six-sigma\<slug>\   （默认位置，可用 SIX_SIGMA_PROJECTS_ROOT 环境变量改）
├── state.json              # 项目状态（程序可读，单一可信源）
├── README.md               # 项目概览（人手可读）
├── define/
│   ├── charter.md
│   ├── sipoc.md
│   ├── voc-ctq.md
│   └── project-plan.md
├── measure/
│   ├── data-collection-plan.md
│   ├── msa-plan.md
│   ├── baseline-data.csv   # 用户上传
│   └── baseline-stats.md   # stats.py 输出
├── analyze/
│   ├── fishbone.md
│   ├── 5why-*.md
│   ├── hypothesis-tests.md
│   ├── pareto.md
│   └── fmea.md
├── improve/
│   ├── solution-matrix.md
│   ├── pilot-plan.md
│   └── doe-results.md
├── control/
│   ├── control-plan.md
│   ├── spc-charts.md
│   └── benefits-tracking.md
└── a3-report.md            # A3 总结（一页可打印）
```

## 状态机

```
[无项目] ──(新建)──> [D 阶段] ──(tollgate1 通过)──> [M 阶段]
                                                       │
                                                       ↓
[结项归档] <─(结项)─ [C 阶段] <─(tollgate4)── [I 阶段] <─(tollgate3)── [A 阶段]
```

每次状态转换：
1. 跑 `references/tollgate-checklist.md` 检查项
2. 通过 → 更新 state.json + 通知
3. 不通过 → 列出缺什么，回到当前阶段

## 自然语言触发 → 动作映射

| 用户说 | 动作 |
|---|---|
| "开始一个 6 Sigma 项目，主题是 X" | 询问基本信息 → `scripts/project-init.py` |
| "填写项目章程" / "继续 charter" | 引导 → 填充 `define/charter.md` |
| "画 SIPOC" | 引导 5 步 → `define/sipoc.md` |
| "做 VOC/CTQ" | 引导 → `define/voc-ctq.md` |
| "进入 M 阶段" / "数据收集计划" | 引导 → `measure/data-collection-plan.md` |
| "算 Cp/Cpk" | 读 CSV → `scripts/stats.py capability` |
| "做 MSA" | 引导 → `measure/msa-plan.md` + stats |
| "画鱼骨图" | 引导 6M → `analyze/fishbone.md` |
| "5 Why" | 引导迭代 → `analyze/5why-X.md` |
| "跑 t 检验" / "假设检验" | 读数据 → `scripts/stats.py test` |
| "Pareto 分析" | 读数据 → `scripts/stats.py pareto` |
| "做 FMEA" | 引导打分 → `analyze/fmea.md` |
| "选方案" | 引导矩阵 → `improve/solution-matrix.md` |
| "做试点计划" | 引导 → `improve/pilot-plan.md` |
| "DOE" | 引导因子水平 → `scripts/stats.py doe` |
| "控制计划" | 引导 → `control/control-plan.md` |
| "A3 报告" | 汇总 → `a3-report.md` + HTML 渲染 |
| "项目状态" | 读 state.json → 输出进度 |

## 统计脚本（`scripts/stats.py`）

**Python 函数**：
- `capability(data, lsl, usl)` → Cp, Cpk, Pp, Ppk, σ
- `t_test_one(data, mu_0)` / `t_test_two(a, b)` / `t_test_paired(a, b)`
- `anova_oneway(*groups)`
- `normality_test(data)` → Shapiro-Wilk + Anderson-Darling
- `sample_size_mean(delta, sigma, alpha, power)` / `sample_size_proportion(p0, p1, alpha, power)`
- `pareto(counts)` → 80/20 累计
- `doe_factorial(factors, levels, response)` → 主效应 + 交互
- `msr_grr(data, part_col, operator_col, value_col)` → GR&R

**CLI 用法**：
```bash
python scripts/stats.py capability --data baseline.csv --lsl 24 --usl 26
python scripts/stats.py ttest --data a.csv --data2 b.csv
python scripts/stats.py normality --data baseline.csv
python scripts/stats.py pareto --data defects.csv --col defect_type
python scripts/stats.py doe --design 2k --factors "A,B,C" --data run.csv
python scripts/stats.py msa --data measure/msa-data.csv --part-col part --operator-col op --value-col meas
python scripts/stats.py sample-size --mode mean --delta 0.5 --sigma 1.0 --alpha 0.05 --power 0.8
```

**依赖**：`numpy`, `scipy`, `pandas`（一次性 `pip install numpy scipy pandas`）

## 关键参考

- DMAIC 五阶段详细指南：`references/dmaic-playbook.md`
- 工具选择表（什么时候用什么工具）：`references/tool-catalog.md`
- 阶段门 review 检查清单：`references/tollgate-checklist.md`

## 编写约定

1. **每个项目独立目录**（不混）
2. **`state.json` 是单一可信源**（阶段进度 + 已完成交付物清单）
3. **模板里用 `<占位符>`**（让 skill 知道要填什么）
4. **统计脚本输出 = Markdown 表格 + 解读**（不裸数字）
5. **A3 报告 = 1 页可打印**（A3 纸 / letter，能贴墙）

## 不做什么

- ❌ 不替你做商业决策（只提供工具和模板）
- ❌ 不连外部 BI / SPC 系统（数据手动导入 CSV）
- ❌ 不做团队协作（无多人编辑、无审批流）
- ❌ 不做实时 SPC 数据采集（输出 SPC chart 模板，用户自己导入数据）

## 维护

- v1.0.0 (2026-10-06): 初版。DMAIC 五阶段完整模板 + stats.py（Cp/Cpk、t 检验、ANOVA、正态性、Pareto、DOE、MSA）+ 状态机。
