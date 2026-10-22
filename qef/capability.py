"""Process capability (Cp, Cpk) and performance (Pp, Ppk) indices, plus
sigma level / DPMO conversion with the conventional 1.5 sigma shift.

Cp / Cpk use the *within-subgroup* (short-term) sigma:
    - subgroups: sigma_within = R-bar / d2            (default)
                 or S-bar / c4                         (method="sbar")
    - individuals: sigma_within = MR-bar / 1.128       (moving range of span 2)
Pp / Ppk use the *overall* (long-term) sample standard deviation (n - 1).

Free online calculators: https://qmsbox.com/cpk and https://qmsbox.com/sigma
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist, mean
from typing import Optional, Sequence, Union

from .control_charts import constants, moving_ranges

_N = NormalDist()

Data = Union[Sequence[float], Sequence[Sequence[float]]]


def _is_subgrouped(data: Data) -> bool:
    return len(data) > 0 and isinstance(data[0], (list, tuple))


def _flatten(data: Data):
    if _is_subgrouped(data):
        return [v for s in data for v in s]
    return list(data)


def overall_sigma(data: Data) -> float:
    """Overall (long-term) sample standard deviation, n - 1 denominator."""
    x = _flatten(data)
    if len(x) < 2:
        raise ValueError("need at least 2 observations")
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def within_sigma(data: Data, method: str = "rbar") -> float:
    """Within-subgroup (short-term) sigma.

    ``data`` is either a flat list of individuals (moving range method) or a
    list of equal-size subgroups (R-bar/d2, or S-bar/c4 with method="sbar").
    """
    if _is_subgrouped(data):
        n = len(data[0])
        if any(len(s) != n for s in data):
            raise ValueError("all subgroups must have the same size")
        k = constants(n)
        if method == "rbar":
            return mean(max(s) - min(s) for s in data) / k["d2"]
        if method == "sbar":
            sbar = mean(overall_sigma(list(s)) for s in data)
            return sbar / k["c4"]
        raise ValueError("method must be 'rbar' or 'sbar'")
    x = list(data)
    if len(x) < 2:
        raise ValueError("need at least 2 observations")
    return mean(moving_ranges(x)) / constants(2)["d2"]


def _index_pair(mu: float, sigma: float, lsl: Optional[float], usl: Optional[float]):
    if lsl is None and usl is None:
        raise ValueError("give at least one specification limit")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    cpu = (usl - mu) / (3 * sigma) if usl is not None else None
    cpl = (mu - lsl) / (3 * sigma) if lsl is not None else None
    c = (usl - lsl) / (6 * sigma) if (usl is not None and lsl is not None) else None
    k = min(v for v in (cpu, cpl) if v is not None)
    return c, k, cpu, cpl


def cp(sigma: float, lsl: float, usl: float) -> float:
    """Cp = (USL - LSL) / (6 * sigma_within)."""
    return (usl - lsl) / (6 * sigma)


def cpk(mu: float, sigma: float, lsl: Optional[float] = None, usl: Optional[float] = None) -> float:
    """Cpk = min(USL - mu, mu - LSL) / (3 * sigma_within). One-sided specs allowed."""
    return _index_pair(mu, sigma, lsl, usl)[1]


# Pp / Ppk are the same formulas evaluated with the overall sigma.
pp = cp
ppk = cpk


@dataclass
class CapabilityResult:
    n: int
    mean: float
    sigma_within: float
    sigma_overall: float
    cp: Optional[float]
    cpk: float
    cpu: Optional[float]
    cpl: Optional[float]
    pp: Optional[float]
    ppk: float
    ppm_expected_overall: float


def capability(
    data: Data,
    lsl: Optional[float] = None,
    usl: Optional[float] = None,
    method: str = "rbar",
) -> CapabilityResult:
    """Full capability study from raw data.

    >>> r = capability([[9, 10, 11], [10, 11, 12], [8, 10, 12]], lsl=4, usl=16)
    >>> round(r.cp, 2)
    1.27
    """
    x = _flatten(data)
    mu = mean(x)
    sw = within_sigma(data, method)
    so = overall_sigma(data)
    c, k, cpu_, cpl_ = _index_pair(mu, sw, lsl, usl)
    p, pk, _, _ = _index_pair(mu, so, lsl, usl)
    ppm = 0.0
    if usl is not None:
        ppm += (1 - _N.cdf((usl - mu) / so)) * 1e6
    if lsl is not None:
        ppm += _N.cdf((lsl - mu) / so) * 1e6
    return CapabilityResult(len(x), mu, sw, so, c, k, cpu_, cpl_, p, pk, ppm)


# ------------------------------------------------------------ sigma / DPMO


def dpmo(defects: float, units: float, opportunities: float = 1) -> float:
    """Defects per million opportunities."""
    return defects / (units * opportunities) * 1e6


def sigma_level(dpmo_value: float, shift: float = 1.5) -> float:
    """Short-term sigma level from long-term DPMO (default 1.5 sigma shift).

    3.4 DPMO -> 6.0 sigma; 66,807 DPMO -> 3.0 sigma.
    """
    if not 0 < dpmo_value < 1e6:
        raise ValueError("DPMO must be between 0 and 1,000,000 (exclusive)")
    return _N.inv_cdf(1 - dpmo_value / 1e6) + shift


def dpmo_from_sigma(sigma: float, shift: float = 1.5) -> float:
    """Long-term DPMO for a short-term sigma level (one-sided, 1.5 sigma shift)."""
    return (1 - _N.cdf(sigma - shift)) * 1e6


def cpk_to_sigma(cpk_value: float) -> float:
    """Z value of the nearer spec limit: Z = 3 * Cpk."""
    return 3 * cpk_value
