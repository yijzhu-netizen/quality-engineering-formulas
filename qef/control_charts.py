"""Shewhart control chart constants, control limits and run rules.

Variables charts: X-bar/R, X-bar/S, I-MR.
Attributes charts: p, np, c, u.
Run rules: Western Electric rules 1-4 and Nelson rules 1-4.

Free online calculators: https://qmsbox.com/xbar-r, https://qmsbox.com/xbar-s,
https://qmsbox.com/p-chart, https://qmsbox.com/np-chart,
https://qmsbox.com/c-chart, https://qmsbox.com/u-chart
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Sequence, Union

# Standard table of control chart constants (ASTM / Montgomery / AIAG SPC manual).
# n: (A2, A3, c4, B3, B4, d2, D3, D4)
_TABLE = {
    2: (1.880, 2.659, 0.7979, 0.000, 3.267, 1.128, 0.000, 3.267),
    3: (1.023, 1.954, 0.8862, 0.000, 2.568, 1.693, 0.000, 2.574),
    4: (0.729, 1.628, 0.9213, 0.000, 2.266, 2.059, 0.000, 2.282),
    5: (0.577, 1.427, 0.9400, 0.000, 2.089, 2.326, 0.000, 2.114),
    6: (0.483, 1.287, 0.9515, 0.030, 1.970, 2.534, 0.000, 2.004),
    7: (0.419, 1.182, 0.9594, 0.118, 1.882, 2.704, 0.076, 1.924),
    8: (0.373, 1.099, 0.9650, 0.185, 1.815, 2.847, 0.136, 1.864),
    9: (0.337, 1.032, 0.9693, 0.239, 1.761, 2.970, 0.184, 1.816),
    10: (0.308, 0.975, 0.9727, 0.284, 1.716, 3.078, 0.223, 1.777),
    11: (0.285, 0.927, 0.9754, 0.321, 1.679, 3.173, 0.256, 1.744),
    12: (0.266, 0.886, 0.9776, 0.354, 1.646, 3.258, 0.283, 1.717),
    13: (0.249, 0.850, 0.9794, 0.382, 1.618, 3.336, 0.307, 1.693),
    14: (0.235, 0.817, 0.9810, 0.406, 1.594, 3.407, 0.328, 1.672),
    15: (0.223, 0.789, 0.9823, 0.428, 1.572, 3.472, 0.347, 1.653),
    16: (0.212, 0.763, 0.9835, 0.448, 1.552, 3.532, 0.363, 1.637),
    17: (0.203, 0.739, 0.9845, 0.466, 1.534, 3.588, 0.378, 1.622),
    18: (0.194, 0.718, 0.9854, 0.482, 1.518, 3.640, 0.391, 1.608),
    19: (0.187, 0.698, 0.9862, 0.497, 1.503, 3.689, 0.403, 1.597),
    20: (0.180, 0.680, 0.9869, 0.510, 1.490, 3.735, 0.415, 1.585),
    21: (0.173, 0.663, 0.9876, 0.523, 1.477, 3.778, 0.425, 1.575),
    22: (0.167, 0.647, 0.9882, 0.534, 1.466, 3.819, 0.434, 1.566),
    23: (0.162, 0.633, 0.9887, 0.545, 1.455, 3.858, 0.443, 1.557),
    24: (0.157, 0.619, 0.9892, 0.555, 1.445, 3.895, 0.451, 1.548),
    25: (0.153, 0.606, 0.9896, 0.565, 1.435, 3.931, 0.459, 1.541),
}
_NAMES = ("A2", "A3", "c4", "B3", "B4", "d2", "D3", "D4")


def constants(n: int) -> Dict[str, float]:
    """Return control chart constants for subgroup size ``n`` (2..25).

    >>> constants(5)["A2"]
    0.577
    """
    if n not in _TABLE:
        raise ValueError("subgroup size n must be between 2 and 25")
    return dict(zip(_NAMES, _TABLE[n]))


def c4_exact(n: int) -> float:
    """Unbiasing constant c4 computed exactly from the gamma function."""
    if n < 2:
        raise ValueError("n must be >= 2")
    return math.sqrt(2.0 / (n - 1)) * math.exp(math.lgamma(n / 2) - math.lgamma((n - 1) / 2))


@dataclass
class Limits:
    """Center line and control limits of one chart."""

    cl: float
    ucl: float
    lcl: float


@dataclass
class VariablesChart:
    """Location chart (X-bar or I) plus dispersion chart (R, S or MR)."""

    location: Limits
    dispersion: Limits
    sigma_within: float


def _check_subgroups(subgroups: Sequence[Sequence[float]]) -> int:
    if len(subgroups) < 2:
        raise ValueError("need at least 2 subgroups")
    sizes = {len(s) for s in subgroups}
    if len(sizes) != 1:
        raise ValueError("all subgroups must have the same size")
    return sizes.pop()


def xbar_r_limits(subgroups: Sequence[Sequence[float]]) -> VariablesChart:
    """X-bar and R chart limits from equal-size subgroups.

    X-bar: CL = X-double-bar, limits = CL +/- A2 * R-bar
    R:     CL = R-bar, UCL = D4 * R-bar, LCL = D3 * R-bar
    sigma_within = R-bar / d2
    """
    n = _check_subgroups(subgroups)
    k = constants(n)
    xbb = mean(mean(s) for s in subgroups)
    rbar = mean(max(s) - min(s) for s in subgroups)
    return VariablesChart(
        location=Limits(xbb, xbb + k["A2"] * rbar, xbb - k["A2"] * rbar),
        dispersion=Limits(rbar, k["D4"] * rbar, k["D3"] * rbar),
        sigma_within=rbar / k["d2"],
    )


def _stdev(x: Sequence[float]) -> float:
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def xbar_s_limits(subgroups: Sequence[Sequence[float]]) -> VariablesChart:
    """X-bar and S chart limits from equal-size subgroups.

    X-bar: CL = X-double-bar, limits = CL +/- A3 * S-bar
    S:     CL = S-bar, UCL = B4 * S-bar, LCL = B3 * S-bar
    sigma_within = S-bar / c4
    """
    n = _check_subgroups(subgroups)
    k = constants(n)
    xbb = mean(mean(s) for s in subgroups)
    sbar = mean(_stdev(s) for s in subgroups)
    return VariablesChart(
        location=Limits(xbb, xbb + k["A3"] * sbar, xbb - k["A3"] * sbar),
        dispersion=Limits(sbar, k["B4"] * sbar, k["B3"] * sbar),
        sigma_within=sbar / k["c4"],
    )


def moving_ranges(x: Sequence[float]) -> List[float]:
    """Moving ranges of span 2: |x[i] - x[i-1]|."""
    return [abs(x[i] - x[i - 1]) for i in range(1, len(x))]


def i_mr_limits(x: Sequence[float]) -> VariablesChart:
    """Individuals and moving range (I-MR) chart limits.

    I:  CL = X-bar, limits = CL +/- 2.66 * MR-bar   (2.66 = 3 / 1.128)
    MR: CL = MR-bar, UCL = 3.267 * MR-bar, LCL = 0
    sigma_within = MR-bar / 1.128
    """
    if len(x) < 2:
        raise ValueError("need at least 2 observations")
    xbar = mean(x)
    mrbar = mean(moving_ranges(x))
    d2 = _TABLE[2][5]
    sigma = mrbar / d2
    return VariablesChart(
        location=Limits(xbar, xbar + 3 * sigma, xbar - 3 * sigma),
        dispersion=Limits(mrbar, _TABLE[2][7] * mrbar, 0.0),
        sigma_within=sigma,
    )


Number = Union[int, float]


def _per_point(n: Union[Number, Sequence[Number]], k: int) -> List[float]:
    if isinstance(n, (int, float)):
        return [float(n)] * k
    if len(n) != k:
        raise ValueError("sample sizes must match the number of points")
    return [float(v) for v in n]


def p_chart_limits(defectives: Sequence[Number], n: Union[Number, Sequence[Number]]) -> List[Limits]:
    """p chart (fraction defective). Returns one Limits per point (n may vary).

    p-bar = sum(d) / sum(n); limits = p-bar +/- 3*sqrt(p-bar(1-p-bar)/n_i), clipped to [0, 1].
    """
    ns = _per_point(n, len(defectives))
    pbar = sum(defectives) / sum(ns)
    out = []
    for ni in ns:
        h = 3 * math.sqrt(pbar * (1 - pbar) / ni)
        out.append(Limits(pbar, min(1.0, pbar + h), max(0.0, pbar - h)))
    return out


def np_chart_limits(defectives: Sequence[Number], n: int) -> Limits:
    """np chart (number defective, constant n).

    CL = n*p-bar; limits = n*p-bar +/- 3*sqrt(n*p-bar*(1-p-bar)), LCL clipped at 0.
    """
    pbar = sum(defectives) / (n * len(defectives))
    cl = n * pbar
    h = 3 * math.sqrt(n * pbar * (1 - pbar))
    return Limits(cl, cl + h, max(0.0, cl - h))


def c_chart_limits(counts: Sequence[Number]) -> Limits:
    """c chart (defects per constant inspection unit). CL = c-bar, limits = c-bar +/- 3*sqrt(c-bar)."""
    cbar = mean(counts)
    h = 3 * math.sqrt(cbar)
    return Limits(cbar, cbar + h, max(0.0, cbar - h))


def u_chart_limits(defects: Sequence[Number], units: Union[Number, Sequence[Number]]) -> List[Limits]:
    """u chart (defects per unit, unit count may vary). Returns one Limits per point.

    u-bar = sum(c) / sum(n); limits = u-bar +/- 3*sqrt(u-bar / n_i), LCL clipped at 0.
    """
    ns = _per_point(units, len(defects))
    ubar = sum(defects) / sum(ns)
    out = []
    for ni in ns:
        h = 3 * math.sqrt(ubar / ni)
        out.append(Limits(ubar, ubar + h, max(0.0, ubar - h)))
    return out


# ---------------------------------------------------------------- run rules


def _zones(x: Sequence[float], cl: float, sigma: float) -> List[float]:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return [(v - cl) / sigma for v in x]


def western_electric_rules(x: Sequence[float], cl: float, sigma: float) -> Dict[int, List[int]]:
    """Western Electric rules 1-4. Returns {rule: [indices of points that trigger it]}.

    1. One point beyond 3 sigma.
    2. Two of three consecutive points beyond 2 sigma, same side.
    3. Four of five consecutive points beyond 1 sigma, same side.
    4. Eight consecutive points on the same side of the center line.
    The index reported is the last point of the offending window.
    """
    z = _zones(x, cl, sigma)
    out: Dict[int, List[int]] = {1: [], 2: [], 3: [], 4: []}
    for i, zi in enumerate(z):
        if abs(zi) > 3:
            out[1].append(i)
        for side in (1, -1):
            if i >= 2 and sum(1 for v in z[i - 2 : i + 1] if side * v > 2) >= 2 and side * zi > 2:
                out[2].append(i)
            if i >= 4 and sum(1 for v in z[i - 4 : i + 1] if side * v > 1) >= 4 and side * zi > 1:
                out[3].append(i)
            if i >= 7 and all(side * v > 0 for v in z[i - 7 : i + 1]):
                out[4].append(i)
    return out


def nelson_rules(x: Sequence[float], cl: float, sigma: float) -> Dict[int, List[int]]:
    """Nelson rules 1-4. Returns {rule: [indices of points that trigger it]}.

    1. One point more than 3 sigma from the center line.
    2. Nine points in a row on the same side of the center line.
    3. Six points in a row steadily increasing or decreasing.
    4. Fourteen points in a row alternating up and down.
    The index reported is the last point of the offending run.
    """
    z = _zones(x, cl, sigma)
    out: Dict[int, List[int]] = {1: [], 2: [], 3: [], 4: []}
    for i, zi in enumerate(z):
        if abs(zi) > 3:
            out[1].append(i)
        if i >= 8 and (all(v > 0 for v in z[i - 8 : i + 1]) or all(v < 0 for v in z[i - 8 : i + 1])):
            out[2].append(i)
        if i >= 5:
            d = [x[j] - x[j - 1] for j in range(i - 4, i + 1)]
            if all(v > 0 for v in d) or all(v < 0 for v in d):
                out[3].append(i)
        if i >= 13:
            d = [x[j] - x[j - 1] for j in range(i - 12, i + 1)]
            if all(v != 0 for v in d) and all(d[j] * d[j - 1] < 0 for j in range(1, len(d))):
                out[4].append(i)
    return out
