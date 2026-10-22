"""Gage R&R by the Average and Range method (AIAG MSA Reference Manual, 4th ed.).

    EV  = R-double-bar * K1                       (repeatability, equipment variation)
    AV  = sqrt((X-diff * K2)^2 - EV^2 / (n * r))  (reproducibility, appraiser variation)
    GRR = sqrt(EV^2 + AV^2)
    PV  = R_p * K3                                (part variation)
    TV  = sqrt(GRR^2 + PV^2)
    %EV = 100 * EV / TV, etc.   %Tolerance = 100 * 6 * GRR / tolerance
    ndc = floor(1.41 * PV / GRR)

n = number of parts, r = number of trials. If the term under the AV root is
negative, AV is set to 0 (as the manual instructs).

Free online calculators: https://qmsbox.com/grr and https://qmsbox.com/msa
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean
from typing import Optional, Sequence

# K1 depends on trials, K2 on appraisers, K3 on parts (AIAG MSA 4th ed., p.118-120).
K1 = {2: 0.8862, 3: 0.5908}
K2 = {2: 0.7071, 3: 0.5231}
K3 = {
    2: 0.7071,
    3: 0.5231,
    4: 0.4467,
    5: 0.4030,
    6: 0.3742,
    7: 0.3534,
    8: 0.3375,
    9: 0.3249,
    10: 0.3146,
}


@dataclass
class GRRResult:
    ev: float
    av: float
    grr: float
    pv: float
    tv: float
    pct_ev: float
    pct_av: float
    pct_grr: float
    pct_pv: float
    ndc: int
    pct_tolerance: Optional[float] = None

    @property
    def verdict(self) -> str:
        """AIAG guideline on %GRR (of total variation)."""
        if self.pct_grr < 10:
            return "acceptable"
        if self.pct_grr <= 30:
            return "conditionally acceptable"
        return "unacceptable"


def grr_from_summary(
    r_double_bar: float,
    x_diff: float,
    r_p: float,
    parts: int,
    trials: int,
    appraisers: int,
    tolerance: Optional[float] = None,
) -> GRRResult:
    """Gage R&R from the summary statistics of the AIAG data sheet."""
    try:
        k1, k2, k3 = K1[trials], K2[appraisers], K3[parts]
    except KeyError as exc:
        raise ValueError(
            "supported: 2-3 trials, 2-3 appraisers, 2-10 parts (AIAG constant tables)"
        ) from exc
    ev = r_double_bar * k1
    av2 = (x_diff * k2) ** 2 - ev**2 / (parts * trials)
    av = math.sqrt(av2) if av2 > 0 else 0.0
    grr = math.sqrt(ev**2 + av**2)
    pv = r_p * k3
    tv = math.sqrt(grr**2 + pv**2)
    ndc = int(1.41 * pv / grr) if grr > 0 else 0
    pct_tol = 100 * 6 * grr / tolerance if tolerance else None
    return GRRResult(
        ev, av, grr, pv, tv,
        100 * ev / tv, 100 * av / tv, 100 * grr / tv, 100 * pv / tv,
        ndc, pct_tol,
    )


def grr_average_range(
    data: Sequence[Sequence[Sequence[float]]], tolerance: Optional[float] = None
) -> GRRResult:
    """Gage R&R from raw data shaped ``data[appraiser][part][trial]``.

    Every appraiser must measure the same parts the same number of times.
    """
    a = len(data)
    n = len(data[0])
    r = len(data[0][0])
    if any(len(op) != n or any(len(p) != r for p in op) for op in data):
        raise ValueError("data must be a full appraiser x part x trial array")
    r_bars = [mean(max(p) - min(p) for p in op) for op in data]
    x_bars = [mean(v for p in op for v in p) for op in data]
    part_means = [mean(v for op in data for v in op[j]) for j in range(n)]
    return grr_from_summary(
        r_double_bar=mean(r_bars),
        x_diff=max(x_bars) - min(x_bars),
        r_p=max(part_means) - min(part_means),
        parts=n,
        trials=r,
        appraisers=a,
        tolerance=tolerance,
    )
