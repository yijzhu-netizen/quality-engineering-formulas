import math

import pytest

from qef.control_charts import (
    _TABLE,
    c4_exact,
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


@pytest.mark.parametrize("n", sorted(_TABLE))
def test_constants_are_self_consistent(n):
    k = constants(n)
    assert k["c4"] == pytest.approx(c4_exact(n), abs=1e-4)
    assert k["A2"] == pytest.approx(3 / (k["d2"] * math.sqrt(n)), abs=2e-3)
    assert k["A3"] == pytest.approx(3 / (k["c4"] * math.sqrt(n)), abs=2e-3)
    s = 3 * math.sqrt(1 - k["c4"] ** 2) / k["c4"]
    assert k["B4"] == pytest.approx(1 + s, abs=2e-3)
    assert k["B3"] == pytest.approx(max(0.0, 1 - s), abs=2e-3)


def test_constants_known_values():
    assert constants(5) == {
        "A2": 0.577, "A3": 1.427, "c4": 0.94, "B3": 0.0, "B4": 2.089,
        "d2": 2.326, "D3": 0.0, "D4": 2.114,
    }
    with pytest.raises(ValueError):
        constants(1)


def test_xbar_r():
    ch = xbar_r_limits([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    assert ch.location.cl == pytest.approx(3)
    assert ch.location.ucl == pytest.approx(3 + 1.023 * 2)
    assert ch.location.lcl == pytest.approx(3 - 1.023 * 2)
    assert ch.dispersion.cl == pytest.approx(2)
    assert ch.dispersion.ucl == pytest.approx(2.574 * 2)
    assert ch.dispersion.lcl == 0
    assert ch.sigma_within == pytest.approx(2 / 1.693)


def test_xbar_s():
    ch = xbar_s_limits([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    assert ch.location.ucl == pytest.approx(3 + 1.954)
    assert ch.dispersion.cl == pytest.approx(1)
    assert ch.dispersion.ucl == pytest.approx(2.568)


def test_i_mr():
    ch = i_mr_limits([10, 12, 11, 13])
    mrbar = 5 / 3
    assert ch.location.cl == pytest.approx(11.5)
    assert ch.location.ucl == pytest.approx(11.5 + 3 * mrbar / 1.128)
    assert ch.dispersion.ucl == pytest.approx(3.267 * mrbar)


def test_p_chart():
    lim = p_chart_limits([2, 4, 6], 100)
    h = 3 * math.sqrt(0.04 * 0.96 / 100)
    assert lim[0].cl == pytest.approx(0.04)
    assert lim[0].ucl == pytest.approx(0.04 + h)
    assert lim[0].lcl == 0.0  # clipped


def test_p_chart_variable_n():
    lim = p_chart_limits([5, 10], [100, 400])
    assert lim[0].cl == pytest.approx(15 / 500)
    assert lim[0].ucl > lim[1].ucl  # smaller sample -> wider limits


def test_np_chart():
    lim = np_chart_limits([2, 4, 6], 100)
    assert lim.cl == pytest.approx(4)
    assert lim.ucl == pytest.approx(4 + 3 * math.sqrt(3.84))


def test_c_chart():
    lim = c_chart_limits([16, 16])
    assert (lim.cl, lim.ucl, lim.lcl) == pytest.approx((16, 28, 4))


def test_u_chart():
    lim = u_chart_limits([10, 20], [5, 5])
    assert lim[0].cl == pytest.approx(3)
    assert lim[0].ucl == pytest.approx(3 + 3 * math.sqrt(3 / 5))


def test_western_electric():
    assert western_electric_rules([0, 0, 3.5, 0], 0, 1)[1] == [2]
    assert western_electric_rules([0, 2.5, 0, 2.5], 0, 1)[2] == [3]
    assert western_electric_rules([0, 2.5, 0, -2.5], 0, 1)[2] == []
    assert western_electric_rules([1.5, 1.5, 0, 1.5, 1.5], 0, 1)[3] == [4]
    assert western_electric_rules([0.5] * 8, 0, 1)[4] == [7]
    assert western_electric_rules([0.5] * 7, 0, 1)[4] == []


def test_nelson():
    assert nelson_rules([-3.1, 0], 0, 1)[1] == [0]
    assert nelson_rules([0.1] * 9, 0, 1)[2] == [8]
    assert nelson_rules([0.1] * 8, 0, 1)[2] == []
    assert nelson_rules([0, 0.1, 0.2, 0.3, 0.4, 0.5], 0, 1)[3] == [5]
    assert nelson_rules([0, 0.1, 0.2, 0.3, 0.4], 0, 1)[3] == []
    zigzag = [0.5 if i % 2 else -0.5 for i in range(14)]
    assert nelson_rules(zigzag, 0, 1)[4] == [13]
    assert nelson_rules(zigzag[:13], 0, 1)[4] == []
