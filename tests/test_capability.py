import math

import pytest

from qef import capability, cp, cpk, dpmo, dpmo_from_sigma, overall_sigma, sigma_level, within_sigma


def test_cp_cpk_known_sigma():
    # mean 10, sigma 1, LSL 7, USL 14: Cp = 7/6, Cpk = min(4, 3)/3 = 1.0
    assert cp(1.0, 7, 14) == pytest.approx(7 / 6)
    assert cpk(10, 1.0, 7, 14) == pytest.approx(1.0)


def test_cpk_one_sided():
    assert cpk(10, 1.0, usl=13) == pytest.approx(1.0)
    assert cpk(10, 0.5, lsl=8) == pytest.approx(4 / 3)
    with pytest.raises(ValueError):
        cpk(10, 1.0)


def test_overall_sigma_textbook():
    # classic example: mean 5, sum of squares 32, n-1 = 7
    assert overall_sigma([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(math.sqrt(32 / 7))


def test_within_sigma_rbar_d2():
    # ranges 2 and 4 -> R-bar 3, d2(n=2) = 1.128
    assert within_sigma([[1, 3], [2, 6]]) == pytest.approx(3 / 1.128)


def test_within_sigma_sbar_c4():
    # s = 1 for both subgroups of size 3 -> S-bar 1, c4(3) = 0.8862
    assert within_sigma([[1, 2, 3], [5, 6, 7]], method="sbar") == pytest.approx(1 / 0.8862)


def test_within_sigma_moving_range():
    # MR = 2, 1, 4 -> MR-bar 7/3
    assert within_sigma([1, 3, 2, 6]) == pytest.approx((7 / 3) / 1.128)


def test_capability_study():
    r = capability([[9, 10, 11], [10, 11, 12], [8, 10, 12]], lsl=4, usl=16)
    sw = (8 / 3) / 1.693
    assert r.n == 9
    assert r.mean == pytest.approx(31 / 3)
    assert r.cp == pytest.approx(12 / (6 * sw))
    assert r.cpk == pytest.approx((16 - 31 / 3) / (3 * sw))
    assert r.pp == pytest.approx(12 / (6 * r.sigma_overall))
    assert r.ppk <= r.pp


def test_sigma_dpmo_table():
    # standard Six Sigma conversion table (1.5 sigma shift)
    assert sigma_level(3.4) == pytest.approx(6.0, abs=0.01)
    assert sigma_level(233) == pytest.approx(5.0, abs=0.01)
    assert sigma_level(6210) == pytest.approx(4.0, abs=0.01)
    assert sigma_level(66807) == pytest.approx(3.0, abs=0.01)
    assert dpmo_from_sigma(6.0) == pytest.approx(3.4, abs=0.1)
    assert dpmo_from_sigma(3.0) == pytest.approx(66807, rel=1e-3)


def test_dpmo():
    assert dpmo(5, 100, 10) == pytest.approx(5000)
