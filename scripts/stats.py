#!/usr/bin/env python3
"""
stats.py — 6 Sigma 统计分析工具

提供常用统计功能的：
1. Python 函数（导入使用）
2. CLI 命令（命令行直接调用）

依赖：numpy, scipy, pandas
安装：pip install numpy scipy pandas
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Sequence

# Windows PowerShell 默认 GBK，stdout reconfigure 为 utf-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import numpy as np
import pandas as pd
from scipy import stats as sp_stats


# ============================================================
# 1. 描述统计
# ============================================================

def describe(data: Sequence[float]) -> dict:
    """描述统计：均值、标准差、中位数、偏度、峰度、范围、IQR"""
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return {"error": "数据为空"}
    q1, q2, q3 = np.percentile(arr, [25, 50, 75])
    return {
        "n": int(len(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)),
        "median": float(q2),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "range": float(np.max(arr) - np.min(arr)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "skew": float(sp_stats.skew(arr)),
        "kurtosis": float(sp_stats.kurtosis(arr)),
    }


# ============================================================
# 2. 过程能力（Cp / Cpk / Pp / Ppk）
# ============================================================

@dataclass
class CapabilityResult:
    n: int
    mean: float
    std_within: float
    std_overall: float
    lsl: float | None
    usl: float | None
    cp: float | None
    cpk: float | None
    pp: float | None
    ppk: float | None
    summary: str


def capability(data: Sequence[float], lsl: float | None = None, usl: float | None = None) -> CapabilityResult:
    """过程能力分析。
    Cp/Cpk = 短期能力（within-subgroup / 移动极差）
    Pp/Ppk = 长期能力（overall std）
    """
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n < 2:
        return CapabilityResult(n=n, mean=float(arr[0]) if n == 1 else 0.0,
                                std_within=0.0, std_overall=0.0,
                                lsl=lsl, usl=usl, cp=None, cpk=None, pp=None, ppk=None,
                                summary="样本量太少（n < 2）")
    mean = float(np.mean(arr))
    # 移动极差估计 within std（sigma_within = MR_bar / d2, d2(n=2) = 1.128）
    mr = np.abs(np.diff(arr))
    mr_bar = float(np.mean(mr))
    sigma_within = mr_bar / 1.128
    sigma_overall = float(np.std(arr, ddof=1))

    cp = cpk = pp = ppk = None
    if lsl is not None and usl is not None and sigma_overall > 0:
        cp = (usl - lsl) / (6 * sigma_within)
        pp = (usl - lsl) / (6 * sigma_overall)
        cpu = (usl - mean) / (3 * sigma_within)
        cpl = (mean - lsl) / (3 * sigma_within)
        cpk = float(min(cpu, cpl))
        ppu = (usl - mean) / (3 * sigma_overall)
        ppl = (mean - lsl) / (3 * sigma_overall)
        ppk = float(min(ppu, ppl))
    elif usl is not None and sigma_overall > 0:
        cp = (usl - mean) / (3 * sigma_within)
        cpk = cp
        pp = (usl - mean) / (3 * sigma_overall)
        ppk = pp
    elif lsl is not None and sigma_overall > 0:
        cp = (mean - lsl) / (3 * sigma_within)
        cpk = cp
        pp = (mean - lsl) / (3 * sigma_overall)
        ppk = pp

    if cpk is None:
        summary = "未提供规格限，无法计算能力指数"
    elif cpk >= 1.67:
        summary = f"Cpk={cpk:.3f}，过程能力优秀（≥ 1.67）✅"
    elif cpk >= 1.33:
        summary = f"Cpk={cpk:.3f}，过程能力良好（≥ 1.33，行业一般要求）✅"
    elif cpk >= 1.0:
        summary = f"Cpk={cpk:.3f}，过程能力勉强（≥ 1.0，但低于行业推荐）⚠️"
    else:
        summary = f"Cpk={cpk:.3f}，过程能力不足（< 1.0），需要改进 ❌"

    return CapabilityResult(
        n=n, mean=mean, std_within=sigma_within, std_overall=sigma_overall,
        lsl=lsl, usl=usl, cp=cp, cpk=cpk, pp=pp, ppk=ppk, summary=summary,
    )


# ============================================================
# 3. 假设检验
# ============================================================

@dataclass
class TestResult:
    test: str
    statistic: float
    p_value: float
    mean_1: float | None
    mean_2: float | None
    effect_size: float | None
    ci_95: tuple | None
    conclusion: str


def t_test_one(data: Sequence[float], mu_0: float, alpha: float = 0.05) -> TestResult:
    """单样本 t 检验：样本均值 vs 已知值"""
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    t, p = sp_stats.ttest_1samp(arr, mu_0)
    n = len(arr)
    mean = float(np.mean(arr))
    se = float(sp_stats.sem(arr))
    ci = (mean - sp_stats.t.ppf(1 - alpha / 2, n - 1) * se,
          mean + sp_stats.t.ppf(1 - alpha / 2, n - 1) * se)
    pooled_std = float(np.std(arr, ddof=1))
    cohen_d = (mean - mu_0) / pooled_std if pooled_std > 0 else 0.0
    conc = "拒绝 H0" if p < alpha else "不能拒绝 H0"
    return TestResult(
        test="单样本 t 检验", statistic=float(t), p_value=float(p),
        mean_1=mean, mean_2=mu_0, effect_size=cohen_d, ci_95=ci,
        conclusion=f"p={p:.4f}, {conc}（α={alpha}）",
    )


def t_test_two(a: Sequence[float], b: Sequence[float], alpha: float = 0.05, equal_var: bool = False) -> TestResult:
    """双样本 t 检验（默认 Welch，不等方差）"""
    a = np.asarray(a, dtype=float); a = a[~np.isnan(a)]
    b = np.asarray(b, dtype=float); b = b[~np.isnan(b)]
    t, p = sp_stats.ttest_ind(a, b, equal_var=equal_var)
    mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
    sd_a, sd_b = float(np.std(a, ddof=1)), float(np.std(b, ddof=1))
    # Cohen's d (pooled)
    sp = math.sqrt(((len(a) - 1) * sd_a ** 2 + (len(b) - 1) * sd_b ** 2) / (len(a) + len(b) - 2))
    cohen_d = (mean_a - mean_b) / sp if sp > 0 else 0.0
    diff = mean_a - mean_b
    se = math.sqrt(sd_a ** 2 / len(a) + sd_b ** 2 / len(b))
    df = (sd_a ** 2 / len(a) + sd_b ** 2 / len(b)) ** 2 / (
        (sd_a ** 2 / len(a)) ** 2 / (len(a) - 1) + (sd_b ** 2 / len(b)) ** 2 / (len(b) - 1)
    )
    ci = (diff - sp_stats.t.ppf(1 - alpha / 2, df) * se,
          diff + sp_stats.t.ppf(1 - alpha / 2, df) * se)
    conc = "拒绝 H0（两组均值显著不同）" if p < alpha else "不能拒绝 H0（两组均值无显著差异）"
    return TestResult(
        test="双样本 t 检验（Welch）" if not equal_var else "双样本 t 检验（等方差）",
        statistic=float(t), p_value=float(p),
        mean_1=mean_a, mean_2=mean_b, effect_size=cohen_d, ci_95=ci,
        conclusion=f"p={p:.4f}, {conc}（α={alpha}）",
    )


def t_test_paired(a: Sequence[float], b: Sequence[float], alpha: float = 0.05) -> TestResult:
    """配对 t 检验（前 / 后对比）"""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    mask = ~(np.isnan(a) | np.isnan(b))
    a, b = a[mask], b[mask]
    t, p = sp_stats.ttest_rel(a, b)
    diff = a - b
    mean_d = float(np.mean(diff))
    sd_d = float(np.std(diff, ddof=1))
    n = len(diff)
    se = sd_d / math.sqrt(n)
    ci = (mean_d - sp_stats.t.ppf(1 - alpha / 2, n - 1) * se,
          mean_d + sp_stats.t.ppf(1 - alpha / 2, n - 1) * se)
    cohen_d = mean_d / sd_d if sd_d > 0 else 0.0
    conc = "拒绝 H0（前后显著不同）" if p < alpha else "不能拒绝 H0（前后无显著差异）"
    return TestResult(
        test="配对 t 检验", statistic=float(t), p_value=float(p),
        mean_1=float(np.mean(a)), mean_2=float(np.mean(b)),
        effect_size=cohen_d, ci_95=ci,
        conclusion=f"p={p:.4f}, {conc}（α={alpha}）",
    )


def anova_oneway(*groups: Sequence[float], alpha: float = 0.05) -> dict:
    """单因素 ANOVA"""
    arrays = [np.asarray(g, dtype=float) for g in groups]
    arrays = [a[~np.isnan(a)] for a in arrays]
    f, p = sp_stats.f_oneway(*arrays)
    conc = "拒绝 H0（至少两组显著不同）" if p < alpha else "不能拒绝 H0（各组均值无显著差异）"
    return {
        "test": "单因素 ANOVA",
        "f_statistic": float(f),
        "p_value": float(p),
        "n_groups": len(arrays),
        "group_sizes": [len(a) for a in arrays],
        "group_means": [float(np.mean(a)) for a in arrays],
        "conclusion": f"p={p:.4f}, {conc}（α={alpha}）",
    }


def normality_test(data: Sequence[float], alpha: float = 0.05) -> dict:
    """正态性检验：Shapiro-Wilk + Anderson-Darling"""
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 3:
        return {"test": "正态性", "conclusion": "样本量太小（n < 3）"}
    sw_stat, sw_p = sp_stats.shapiro(arr)
    ad = sp_stats.anderson(arr, dist="norm")
    sw_conc = "拒绝正态性" if sw_p < alpha else "不能拒绝正态性"
    return {
        "test": "正态性检验",
        "n": len(arr),
        "shapiro_wilk": {"statistic": float(sw_stat), "p_value": float(sw_p),
                         "conclusion": f"p={sw_p:.4f}, {sw_conc}（α={alpha}）"},
        "anderson_darling": {"statistic": float(ad.statistic),
                             "critical_values": ad.critical_values.tolist(),
                             "significance_levels": ad.significance_level.tolist()},
        "interpretation": "数据呈正态分布 ✅" if sw_p >= alpha else "数据**不**呈正态分布 ⚠️（考虑非参数检验或 Box-Cox 变换）",
    }


def chi2_test(observed: Sequence[int], expected: Sequence[float] | None = None) -> dict:
    """卡方检验（拟合优度 / 独立性）"""
    obs = np.asarray(observed, dtype=float)
    if expected is None:
        exp = np.full_like(obs, np.mean(obs))
    else:
        exp = np.asarray(expected, dtype=float)
    chi2, p = sp_stats.chisquare(obs, exp)
    return {"test": "卡方检验", "chi2": float(chi2), "p_value": float(p),
            "conclusion": f"p={p:.4f}, " + ("拒绝 H0（观测与期望显著不同）" if p < 0.05 else "不能拒绝 H0")}


# ============================================================
# 4. 样本量计算
# ============================================================

def sample_size_mean(delta: float, sigma: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """样本量（连续型，mean）：检测 delta 差异，power=0.8"""
    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)
    z_beta = sp_stats.norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) * sigma / delta) ** 2
    return int(math.ceil(n))


def sample_size_proportion(p0: float, p1: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """样本量（比例）：从 p0 改到 p1"""
    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)
    z_beta = sp_stats.norm.ppf(power)
    p_bar = (p0 + p1) / 2
    n = ((z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) / (p1 - p0)) ** 2
    return int(math.ceil(n))


# ============================================================
# 5. Pareto 分析
# ============================================================

def pareto(counts: dict) -> dict:
    """Pareto 分析：80/20 累计"""
    items = sorted(counts.items(), key=lambda x: -x[1])
    total = sum(v for _, v in items)
    if total == 0:
        return {"data": [], "total": 0, "critical_few": []}
    cum = 0
    out = []
    for name, count in items:
        cum += count
        out.append({
            "category": str(name),
            "count": int(count),
            "percent": count / total * 100,
            "cumulative_percent": cum / total * 100,
        })
    critical_few = [r for r in out if r["cumulative_percent"] <= 80]
    return {"data": out, "total": total, "critical_few": [r["category"] for r in critical_few]}


# ============================================================
# 6. DOE（2^k 因子设计，主效应 + 交互）
# ============================================================

def doe_factorial(data: pd.DataFrame, factors: list, response: str) -> dict:
    """2^k 全因子设计的主效应 + 交互。

    data: 包含 factors 列 + response 列的 DataFrame
    factors: 因子列名列表（如 ['A', 'B', 'C']）
    response: 响应列名
    """
    df = data.copy()
    for f in factors:
        df[f] = df[f].astype("category")
    # 主效应：每个因子的水平均值差
    main_effects = {}
    for f in factors:
        levels = df.groupby(f, observed=True)[response].mean()
        main_effects[f] = {str(k): float(v) for k, v in levels.items()}
    # 2 阶交互
    interactions = {}
    for i, f1 in enumerate(factors):
        for f2 in factors[i + 1:]:
            interaction = df.groupby([f1, f2], observed=True)[response].mean()
            interactions[f"{f1}×{f2}"] = {
                f"{str(k1)},{str(k2)}": float(v) for (k1, k2), v in interaction.items()
            }
    return {
        "factors": factors,
        "response": response,
        "n_runs": len(df),
        "main_effects": main_effects,
        "interactions": interactions,
        "note": "主效应：水平均值差越大，因子影响越大；交互：联合效应",
    }


# ============================================================
# 7. MSA / GR&R（简化版：Range method）
# ============================================================

def msr_grr(data: pd.DataFrame, part_col: str, operator_col: str, value_col: str, tolerance: float | None = None) -> dict:
    """GR&R 分析（Range method 简化版）。

    data: 包含 part / operator / measurement 三列
    """
    df = data.copy()
    # Repeatability (EV) = R_bar / d2 (d2=1.128 for n=2)
    ranges = df.groupby([part_col, operator_col])[value_col].agg(lambda x: x.max() - x.min())
    r_bar = ranges.mean()
    EV = r_bar / 1.128  # n=2 trials
    # Reproducibility (AV) = X_diff * K1
    operator_means = df.groupby(operator_col)[value_col].mean()
    R_x = operator_means.max() - operator_means.min()
    K1 = 0.707  # for 3 operators
    AV = R_x * K1
    # Part Variation (PV) = R_part * K2
    part_ranges = df.groupby(part_col)[value_col].agg(lambda x: x.max() - x.min())
    R_part = part_ranges.mean()
    K2 = 0.523  # for 10 parts
    PV = R_part * K2
    # GR&R
    GRR = math.sqrt(EV ** 2 + AV ** 2)
    TV = math.sqrt(GRR ** 2 + PV ** 2)
    pct_EV = EV / TV * 100 if TV > 0 else 0
    pct_AV = AV / TV * 100 if TV > 0 else 0
    pct_PV = PV / TV * 100 if TV > 0 else 0
    pct_GRR = GRR / TV * 100 if TV > 0 else 0
    # %Tolerance
    pct_tol = GRR / tolerance * 100 if tolerance and tolerance > 0 else None

    if pct_GRR < 10:
        verdict = f"%GR&R={pct_GRR:.1f}%，量具系统优秀 ✅"
    elif pct_GRR < 30:
        verdict = f"%GR&R={pct_GRR:.1f}%，量具系统视情况可接受 ⚠️"
    else:
        verdict = f"%GR&R={pct_GRR:.1f}%，量具系统**不可接受**，需改进 ❌"

    return {
        "EV": float(EV), "AV": float(AV), "PV": float(PV), "GRR": float(GRR), "TV": float(TV),
        "pct_EV": float(pct_EV), "pct_AV": float(pct_AV), "pct_PV": float(pct_PV),
        "pct_GRR": float(pct_GRR), "pct_tolerance": pct_tol,
        "verdict": verdict,
    }


# ============================================================
# CLI
# ============================================================

def read_csv_column(path: str, column: str | None = None) -> np.ndarray:
    df = pd.read_csv(path)
    if column is None:
        if df.shape[1] == 1:
            return df.iloc[:, 0].dropna().values
        raise ValueError("CSV 多列时需要 --col 指定")
    return df[column].dropna().values


def main():
    parser = argparse.ArgumentParser(description="6 Sigma 统计分析 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # describe
    s = sub.add_parser("describe", help="描述统计")
    s.add_argument("--data", required=True)
    s.add_argument("--col")

    # capability
    s = sub.add_parser("capability", help="Cp/Cpk/Pp/Ppk")
    s.add_argument("--data", required=True)
    s.add_argument("--col")
    s.add_argument("--lsl", type=float)
    s.add_argument("--usl", type=float)

    # ttest
    s = sub.add_parser("ttest", help="t 检验")
    s.add_argument("--data", required=True, help="CSV：mode=two/paired 时用")
    s.add_argument("--col")
    s.add_argument("--data2")
    s.add_argument("--col2")
    s.add_argument("--mode", choices=["one", "two", "paired"], default="two")
    s.add_argument("--mu0", type=float, help="mode=one 时已知均值")
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--equal-var", action="store_true")

    # anova
    s = sub.add_parser("anova", help="单因素 ANOVA")
    s.add_argument("--data", required=True)
    s.add_argument("--value-col", required=True)
    s.add_argument("--group-col", required=True)

    # normality
    s = sub.add_parser("normality", help="正态性检验")
    s.add_argument("--data", required=True)
    s.add_argument("--col")

    # chi2
    s = sub.add_parser("chi2", help="卡方检验")
    s.add_argument("--observed", nargs="+", type=int, required=True)
    s.add_argument("--expected", nargs="+", type=float)

    # sample-size
    s = sub.add_parser("sample-size", help="样本量计算")
    s.add_argument("--mode", choices=["mean", "proportion"], required=True)
    s.add_argument("--delta", type=float, help="mean: 期望差异")
    s.add_argument("--sigma", type=float, help="mean: 标准差")
    s.add_argument("--p0", type=float, help="proportion: 起始比例")
    s.add_argument("--p1", type=float, help="proportion: 目标比例")
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--power", type=float, default=0.8)

    # pareto
    s = sub.add_parser("pareto", help="Pareto 分析")
    s.add_argument("--data", required=True)
    s.add_argument("--col", required=True)

    # doe
    s = sub.add_parser("doe", help="DOE 2^k 主效应")
    s.add_argument("--data", required=True)
    s.add_argument("--factors", required=True, help="逗号分隔，如 'A,B,C'")
    s.add_argument("--response", required=True)

    # msa
    s = sub.add_parser("msa", help="MSA / GR&R")
    s.add_argument("--data", required=True)
    s.add_argument("--part-col", required=True)
    s.add_argument("--operator-col", required=True)
    s.add_argument("--value-col", required=True)
    s.add_argument("--tolerance", type=float)

    args = parser.parse_args()

    if args.cmd == "describe":
        arr = read_csv_column(args.data, args.col)
        print(json.dumps(describe(arr), ensure_ascii=False, indent=2))
    elif args.cmd == "capability":
        arr = read_csv_column(args.data, args.col)
        r = capability(arr, args.lsl, args.usl)
        print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
    elif args.cmd == "ttest":
        alpha = args.alpha
        if args.mode == "one":
            arr = read_csv_column(args.data, args.col)
            r = t_test_one(arr, args.mu0, alpha)
        elif args.mode == "two":
            a = read_csv_column(args.data, args.col)
            b = read_csv_column(args.data2, args.col2)
            r = t_test_two(a, b, alpha, equal_var=args.equal_var)
        else:  # paired
            a = read_csv_column(args.data, args.col)
            b = read_csv_column(args.data2, args.col2)
            r = t_test_paired(a, b, alpha)
        print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
    elif args.cmd == "anova":
        df = pd.read_csv(args.data)
        groups = [g[args.value_col].dropna().values for _, g in df.groupby(args.group_col)]
        print(json.dumps(anova_oneway(*groups), ensure_ascii=False, indent=2))
    elif args.cmd == "normality":
        arr = read_csv_column(args.data, args.col)
        print(json.dumps(normality_test(arr), ensure_ascii=False, indent=2))
    elif args.cmd == "chi2":
        print(json.dumps(chi2_test(args.observed, args.expected), ensure_ascii=False, indent=2))
    elif args.cmd == "sample-size":
        if args.mode == "mean":
            n = sample_size_mean(args.delta, args.sigma, args.alpha, args.power)
        else:
            n = sample_size_proportion(args.p0, args.p1, args.alpha, args.power)
        print(json.dumps({"mode": args.mode, "n": n, "alpha": args.alpha, "power": args.power},
                         ensure_ascii=False, indent=2))
    elif args.cmd == "pareto":
        df = pd.read_csv(args.data)
        counts = df[args.col].value_counts().to_dict()
        print(json.dumps(pareto(counts), ensure_ascii=False, indent=2))
    elif args.cmd == "doe":
        df = pd.read_csv(args.data)
        factors = [f.strip() for f in args.factors.split(",")]
        print(json.dumps(doe_factorial(df, factors, args.response), ensure_ascii=False, indent=2))
    elif args.cmd == "msa":
        df = pd.read_csv(args.data)
        print(json.dumps(msr_grr(df, args.part_col, args.operator_col, args.value_col, args.tolerance),
                         ensure_ascii=False, indent=2))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
