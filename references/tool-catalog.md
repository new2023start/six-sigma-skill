# 工具选择表（Tool Catalog）

> 6 Sigma 常用工具 + 何时用 + 产出位置速查。

## D — Define 阶段

| 工具 | 何时用 | 产出 |
|---|---|---|
| 项目章程 (Charter) | 项目立项 | `define/charter.md` |
| SIPOC | 流程边界不清 | `define/sipoc.md` |
| VOC 收集 | 不了解客户 | 访谈 / 投诉 / 调研记录 |
| CTQ 树 | VOC → 可测量指标 | `define/voc-ctq.md` |
| RACI | 角色不清 | `define/project-plan.md` 干系人段 |
| 头脑风暴 | 想法收集 | 会议纪要 |
| 亲和图 (Affinity) | 大量定性数据分组 | 阶段总结 |
| Kano 模型 | VOC 优先级（基本/期望/兴奋） | `define/voc-ctq.md` 优先级 |

## M — Measure 阶段

| 工具 | 何时用 | 产出 |
|---|---|---|
| 数据收集计划 (DCP) | 需要系统化采样 | `measure/data-collection-plan.md` |
| 操作定义 (Operational Definition) | CTQ 有歧义 | CTQ 文档附录 |
| MSA（GR&R） | 测量系统不确定 | `measure/msa-plan.md` + 统计输出 |
| Cp/Cpk | 连续型数据 | `scripts/stats.py capability` |
| Pp/Ppk | 短期 / 长期能力 | 同上 |
| 正态性检验 | 不知道分布 | `scripts/stats.py normality` |
| 样本量计算 | 不知该采多少 | `scripts/stats.py sample-size` |
| 控制图（基线） | 过程稳定性初判 | I-MR / Xbar-R |
| 直方图 + 箱线图 | 分布形状 | `scripts/stats.py describe` |

## A — Analyze 阶段

| 工具 | 何时用 | 产出 |
|---|---|---|
| 鱼骨图 (Ishikawa) | 找潜在根因 | `analyze/fishbone.md`（6M：Man/Machine/Material/Method/Measurement/Environment） |
| 5 Why | 单一问题深挖 | `analyze/5why-<topic>.md` |
| Pareto | 找关键少数 | `scripts/stats.py pareto` |
| 假设检验 | 验证根因 | `scripts/stats.py ttest / anova / chi2` |
| 相关性 / 回归 | 找 X-Y 关系 | `scripts/stats.py correlate` |
| FMEA | 风险评估 | `analyze/fmea.md` |
| 多变量图 (Multi-Vari) | 因素分层 | 散点图 |
| 时间序列 | 趋势 / 周期 | 控制图 |
| 流程图 (Process Map) | 理解细节 | 流程图 |

## I — Improve 阶段

| 工具 | 何时用 | 产出 |
|---|---|---|
| 头脑风暴 | 方案生成 | 会议纪要 |
| 方案选择矩阵 | 多方案筛选 | `improve/solution-matrix.md` |
| 试点 (Pilot) | 验证方案 | `improve/pilot-plan.md` + 结果分析 |
| DOE（2^k） | 优化多个因子 | `scripts/stats.py doe` |
| 响应曲面 (RSM) | 找最优参数 | 同上 |
| 防错 (Poka-Yoke) | 防失效 | 改进方案 |
| 标准化 (Standardization) | 文档化 | SOP 更新 |
| 拉系统 (Pull) | 库存 / 流动 | 改进方案 |

## C — Control 阶段

| 工具 | 何时用 | 产出 |
|---|---|---|
| 控制计划 (Control Plan) | 标准化控制 | `control/control-plan.md` |
| SPC 控制图 | 持续监控 | `control/spc-charts.md` |
| 反应计划 (Reaction Plan) | 异常响应 | 控制计划附录 |
| PFMEA | 失效预防 | 更新 FMEA |
| 作业指导书 (SOP) | 操作标准化 | 文档更新 |
| 培训 | 知识传递 | 培训记录 |
| 收益追踪 | 财务验证 | `control/benefits-tracking.md` |
| 项目结项 | 关闭项目 | `a3-report.md` |

---

## 工具选择决策树

```
你的问题是什么？
│
├── 不知道流程长什么样 → SIPOC / 流程图
├── 不知道客户要什么 → VOC / Kano / CTQ 树
├── 不知道现状有多差 → 数据收集 + 控制图 + Cp/Cpk
├── 不知道数据可不可信 → MSA（GR&R）
├── 不知道根本原因 → 鱼骨图 + 5 Why + 假设检验
├── 不知道哪些原因最关键 → Pareto + FMEA
├── 解决方案太多 → 方案选择矩阵
├── 不知道方案有没有效 → 试点 + 假设检验
├── 不知道最优参数 → DOE
├── 改进后保持不住 → 控制计划 + SPC + 反应计划
└── 不知道是否赚到 → 收益追踪
```

---

## 参考书目

- George et al., *The Lean Six Sigma Pocket Toolbook*
- Pyzdek & Keller, *The Six Sigma Handbook*
- ASQ Certified Six Sigma Black Belt BOK
