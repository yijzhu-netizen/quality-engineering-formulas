"""quality-engineering-formulas: Cpk/Ppk, SPC control charts and Gage R&R in pure Python.

Free online calculators for every formula: https://qmsbox.com
"""

from .capability import (
    capability,
    cp,
    cpk,
    cpk_to_sigma,
    dpmo,
    dpmo_from_sigma,
    overall_sigma,
    pp,
    ppk,
    sigma_level,
    within_sigma,
)
from .control_charts import (
    c_chart_limits,
    constants,
    i_mr_limits,
    nelson_rules,
    np_chart_limits,
    p_chart_limits,
    u_chart_limits,
    western_electric_rules,
    xbar_r_limits,
    xbar_s_limits,
)
from .grr import grr_average_range, grr_from_summary

__version__ = "0.1.0"

__all__ = [
    "capability", "cp", "cpk", "pp", "ppk", "within_sigma", "overall_sigma",
    "dpmo", "sigma_level", "dpmo_from_sigma", "cpk_to_sigma",
    "constants", "xbar_r_limits", "xbar_s_limits", "i_mr_limits",
    "p_chart_limits", "np_chart_limits", "c_chart_limits", "u_chart_limits",
    "western_electric_rules", "nelson_rules",
    "grr_average_range", "grr_from_summary",
]
