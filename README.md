# quality-engineering-formulas

**Open-source Cpk/Ppk, SPC control chart, Gage R&R and Six Sigma formulas in pure Python — with free online calculators at [qmsbox.com](https://qmsbox.com).**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

A small, readable, zero-dependency reference implementation of the statistics quality engineers use every day
(AIAG SPC / MSA manuals, IATF 16949, Six Sigma). Every formula is written out in the docstring and covered by
tests that use textbook numbers you can check by hand — including the AIAG MSA 4th edition Gage R&R worked example.

If you just need an answer and not code, every formula here has a matching **free online calculator** on
[QMSBox](https://qmsbox.com) (no install, free once per day per tool).

## What's inside

| Module | Contents |
|---|---|
| `qef.capability` | Cp, Cpk, Pp, Ppk, CPU/CPL, within sigma (R̄/d2, S̄/c4, moving range), overall sigma, expected PPM, DPMO ↔ sigma level (1.5σ shift) |
| `qef.control_charts` | Constants table A2, A3, B3, B4, c4, d2, D3, D4 for n = 2…25; X̄-R, X̄-S, I-MR, p, np, c, u chart limits; Western Electric rules 1–4 and Nelson rules 1–4 |
| `qef.grr` | Gage R&R by the Average & Range method (AIAG MSA 4th ed.): EV, AV, GRR, PV, TV, %EV/%AV/%GRR/%PV, %Tolerance, ndc, verdict |

## Install

```bash
pip install git+https://github.com/yijzhu-netizen/quality-engineering-formulas.git
```

Requires Python 3.8+. No third-party dependencies (only the standard library `statistics` module).

## Usage

### Process capability (Cp, Cpk, Pp, Ppk)

```python
from qef import capability

subgroups = [
    [9.98, 10.02, 10.01, 9.99, 10.00],
    [10.03, 9.97, 10.00, 10.02, 9.99],
    [10.01, 10.00, 9.98, 10.02, 10.01],
    [9.99, 10.01, 10.03, 9.98, 10.00],
]
r = capability(subgroups, lsl=9.90, usl=10.10)   # sigma_within = R-bar / d2
print(round(r.cp, 2), round(r.cpk, 2), round(r.pp, 2), round(r.ppk, 2))
# 1.63 1.6 1.92 1.88
```

Pass a flat list instead of subgroups and the within sigma is estimated from the moving range (MR̄ / 1.128).
Use `method="sbar"` for S̄ / c4.

### Control chart limits

```python
from qef import xbar_r_limits, p_chart_limits, nelson_rules

ch = xbar_r_limits(subgroups)
ch.location     # Limits(cl=10.002, ucl=10.0294, lcl=9.9746)   X-bar chart
ch.dispersion   # Limits(cl=0.0475, ucl=0.1004, lcl=0.0)       R chart

p_chart_limits([3, 5, 2, 4], 200)[0]   # Limits(cl=0.0175, ucl=0.0453, lcl=0.0)

nelson_rules([10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6], cl=10.0, sigma=0.5)
# {1: [], 2: [], 3: [5, 6], 4: []}   -> six points steadily increasing
```

### Gage R&R (AIAG average & range method)

```python
from qef import grr_from_summary, grr_average_range

# AIAG MSA 4th edition example: 3 appraisers x 10 parts x 3 trials
g = grr_from_summary(r_double_bar=0.3417, x_diff=0.4446, r_p=3.511,
                     parts=10, trials=3, appraisers=3)
round(g.pct_grr, 2), g.ndc, g.verdict
# (26.68, 5, 'conditionally acceptable')

# or straight from raw data shaped data[appraiser][part][trial]
g = grr_average_range(data, tolerance=0.5)
```

### Sigma level and DPMO

```python
from qef import sigma_level, dpmo, dpmo_from_sigma

sigma_level(3.4)        # 6.0
sigma_level(6210)       # 4.0
dpmo(defects=5, units=100, opportunities=10)   # 5000.0
```

## Formula → free online calculator

| Formula / method | Free online calculator |
|---|---|
| Cp, Cpk, Pp, Ppk process capability | [qmsbox.com/cpk](https://qmsbox.com/cpk) |
| X̄-R control chart (A2, D3, D4) | [qmsbox.com/xbar-r](https://qmsbox.com/xbar-r) |
| X̄-S control chart (A3, B3, B4) | [qmsbox.com/xbar-s](https://qmsbox.com/xbar-s) |
| p chart (fraction defective) | [qmsbox.com/p-chart](https://qmsbox.com/p-chart) |
| np chart (number defective) | [qmsbox.com/np-chart](https://qmsbox.com/np-chart) |
| c chart (defects count) | [qmsbox.com/c-chart](https://qmsbox.com/c-chart) |
| u chart (defects per unit) | [qmsbox.com/u-chart](https://qmsbox.com/u-chart) |
| Gage R&R (average & range / ANOVA) | [qmsbox.com/grr](https://qmsbox.com/grr) |
| MSA (bias, linearity, stability, attribute agreement) | [qmsbox.com/msa](https://qmsbox.com/msa) |
| Sigma level ↔ DPMO | [qmsbox.com/sigma](https://qmsbox.com/sigma) |
| Normality test (before running Cpk) | [qmsbox.com/normality](https://qmsbox.com/normality) |
| FMEA (RPN / AIAG-VDA Action Priority) | [qmsbox.com/fmea](https://qmsbox.com/fmea) |
| 8D problem solving report | [qmsbox.com/8d](https://qmsbox.com/8d) |
| DOE full factorial | [qmsbox.com/doe-full](https://qmsbox.com/doe-full) |
| Sample size | [qmsbox.com/sample-size](https://qmsbox.com/sample-size) |

## Acceptance criteria cheat sheet

| Metric | Guideline |
|---|---|
| Cpk / Ppk (ongoing production) | ≥ 1.33 |
| Ppk (initial process study, PPAP / IATF 16949) | ≥ 1.67 |
| Cpk for safety / critical characteristics | often ≥ 1.67 (check customer-specific requirements) |
| %GRR (of total variation or tolerance) | < 10 % acceptable · 10–30 % conditionally acceptable · > 30 % unacceptable |
| ndc (number of distinct categories) | ≥ 5 |
| Six Sigma | 6σ ≈ 3.4 DPMO (with 1.5σ shift) · 4σ ≈ 6,210 DPMO · 3σ ≈ 66,807 DPMO |

Notes: Cp/Cpk use within-subgroup sigma and are only meaningful for a process in statistical control;
Pp/Ppk use the overall sample standard deviation. Both assume approximately normal data — test normality first.

## Running the tests

```bash
pip install pytest
pytest --doctest-modules qef tests
```

## Also see

Other open-source quality / SPC projects worth knowing:

- [carlosqsilva/pyspc](https://github.com/carlosqsilva/pyspc) — Statistical Process Control charts library for Python
- [luca-scr/qcc](https://github.com/luca-scr/qcc) — the classic R package for quality control charts
- [owodunni/GageRnR](https://github.com/owodunni/GageRnR) — Gage R&R calculation in Python
- [huft-jonathan/pyshewhart](https://github.com/huft-jonathan/pyshewhart) — Shewhart control charts in Python
- [jjmartegarcia/sixsigmaspc](https://github.com/jjmartegarcia/sixsigmaspc) — Six Sigma SPC library
- [AUS-DOH-Safety-and-Quality/PowerBI-SPC](https://github.com/AUS-DOH-Safety-and-Quality/PowerBI-SPC) — open-source Power BI visual for SPC charts
- [diribet/cpknextgen](https://github.com/diribet/cpknextgen) — Cp/Cpk estimation with uncertainty

## Contributing

Issues and pull requests are welcome — especially more textbook examples for the tests, ANOVA Gage R&R,
and non-normal capability. Please keep the library dependency-free and every formula documented.

## License

[MIT](LICENSE) © 2026 QMSBox

---

## 中文说明

**quality-engineering-formulas** 是一个开源、零依赖的 Python 质量工程公式库，包含：

- **过程能力**：Cp、Cpk、Pp、Ppk（组内标准差 R̄/d2、S̄/c4 或移动极差；整体标准差），西格玛水平 ↔ DPMO 换算（1.5σ 偏移）
- **SPC 控制图**：n=2–25 控制图系数表（A2、A3、B3、B4、c4、d2、D3、D4），X̄-R、X̄-S、I-MR、p、np、c、u 图控制限，西电判异准则 1–4 与 Nelson 判异准则 1–4
- **量具 GR&R**：AIAG MSA 第四版均值极差法（EV、AV、GRR、PV、TV、%GRR、ndc）

所有公式都有可手算验证的测试用例（包括 AIAG MSA 第四版 GR&R 官方示例）。

不想写代码？每个公式都可以在 **[质量工具箱 QMSBox（qmsbox.com）](https://qmsbox.com)** 上在线免费计算：
[Cpk 计算器](https://qmsbox.com/cpk) · [X̄-R 控制图](https://qmsbox.com/xbar-r) · [GR&R](https://qmsbox.com/grr) ·
[MSA](https://qmsbox.com/msa) · [FMEA](https://qmsbox.com/fmea) · [8D 报告](https://qmsbox.com/8d) · [DOE](https://qmsbox.com/doe-full)，每个工具每天可免费使用一次。

判定标准速查：Cpk ≥ 1.33（量产），≥ 1.67（IATF 16949 初始过程研究）；%GRR < 10% 可接受，10–30% 有条件接受，> 30% 不可接受；ndc ≥ 5。

更多中文说明见 [README.zh-CN.md](README.zh-CN.md)。
