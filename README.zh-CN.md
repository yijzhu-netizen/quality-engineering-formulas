# quality-engineering-formulas（质量工程公式库）

开源、零依赖的 Python 质量工程公式库：**Cpk/Ppk 过程能力、SPC 控制图、量具 GR&R、六西格玛**。
配套免费在线计算器：**[质量工具箱 QMSBox — qmsbox.com](https://qmsbox.com)**（无需安装，每个工具每天免费一次）。

## 安装

```bash
pip install git+https://github.com/yijzhu-netizen/quality-engineering-formulas.git
```

## 快速示例

```python
from qef import capability, xbar_r_limits, grr_from_summary, sigma_level

r = capability([[9.98, 10.02, 10.01, 9.99, 10.00],
                [10.03, 9.97, 10.00, 10.02, 9.99]], lsl=9.90, usl=10.10)
print(r.cp, r.cpk, r.pp, r.ppk)

g = grr_from_summary(0.3417, 0.4446, 3.511, parts=10, trials=3, appraisers=3)
print(g.pct_grr, g.ndc, g.verdict)   # 26.68  5  conditionally acceptable

print(sigma_level(3.4))              # 6.0
```

## 公式与在线计算器对照

| 公式 / 方法 | 在线计算器 |
|---|---|
| Cp、Cpk、Pp、Ppk | [qmsbox.com/cpk](https://qmsbox.com/cpk) |
| X̄-R / X̄-S 控制图 | [qmsbox.com/xbar-r](https://qmsbox.com/xbar-r) · [qmsbox.com/xbar-s](https://qmsbox.com/xbar-s) |
| p / np / c / u 图 | [p](https://qmsbox.com/p-chart) · [np](https://qmsbox.com/np-chart) · [c](https://qmsbox.com/c-chart) · [u](https://qmsbox.com/u-chart) |
| 量具 GR&R / MSA | [qmsbox.com/grr](https://qmsbox.com/grr) · [qmsbox.com/msa](https://qmsbox.com/msa) |
| 西格玛水平 / DPMO | [qmsbox.com/sigma](https://qmsbox.com/sigma) |
| 正态性检验 | [qmsbox.com/normality](https://qmsbox.com/normality) |
| FMEA / 8D / DOE / 样本量 | [FMEA](https://qmsbox.com/fmea) · [8D](https://qmsbox.com/8d) · [DOE](https://qmsbox.com/doe-full) · [样本量](https://qmsbox.com/sample-size) |

## 判定标准速查

- Cpk/Ppk ≥ 1.33（量产）；初始过程研究 Ppk ≥ 1.67（PPAP / IATF 16949）
- %GRR：< 10% 可接受；10%–30% 有条件接受；> 30% 不可接受
- ndc（可区分类别数）≥ 5
- 6σ ≈ 3.4 DPMO；4σ ≈ 6,210 DPMO；3σ ≈ 66,807 DPMO（含 1.5σ 偏移）

许可证：MIT © 2026 QMSBox
