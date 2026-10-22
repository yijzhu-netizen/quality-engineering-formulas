import math

import pytest

from qef import grr_average_range, grr_from_summary


def test_aiag_msa_4th_edition_example():
    # AIAG MSA 4th ed. worked example: 3 appraisers, 10 parts, 3 trials
    r = grr_from_summary(r_double_bar=0.3417, x_diff=0.4446, r_p=3.511,
                         parts=10, trials=3, appraisers=3)
    assert r.ev == pytest.approx(0.20188, abs=1e-4)
    assert r.av == pytest.approx(0.22963, abs=1e-4)
    assert r.grr == pytest.approx(0.30575, abs=1e-4)
    assert r.pv == pytest.approx(1.10456, abs=1e-4)
    assert r.tv == pytest.approx(1.14610, abs=1e-4)
    assert r.pct_ev == pytest.approx(17.62, abs=0.02)
    assert r.pct_av == pytest.approx(20.04, abs=0.02)
    assert r.pct_grr == pytest.approx(26.68, abs=0.02)
    assert r.pct_pv == pytest.approx(96.38, abs=0.02)
    assert r.ndc == 5
    assert r.verdict == "conditionally acceptable"


def test_av_clipped_to_zero():
    r = grr_from_summary(r_double_bar=1.0, x_diff=0.0, r_p=5.0, parts=5, trials=2, appraisers=2)
    assert r.av == 0.0
    assert r.grr == pytest.approx(r.ev)


def test_raw_data_matches_hand_summary():
    # data[appraiser][part][trial]
    data = [
        [[10.0, 10.2], [12.0, 12.1], [14.0, 13.8]],
        [[10.3, 10.1], [12.4, 12.2], [14.1, 14.3]],
    ]
    r_bar_a = (0.2 + 0.1 + 0.2) / 3
    r_bar_b = (0.2 + 0.2 + 0.2) / 3
    x_a = sum(v for p in data[0] for v in p) / 6
    x_b = sum(v for p in data[1] for v in p) / 6
    parts = [sum(data[a][j][t] for a in range(2) for t in range(2)) / 4 for j in range(3)]
    expected = grr_from_summary((r_bar_a + r_bar_b) / 2, abs(x_a - x_b),
                                max(parts) - min(parts), parts=3, trials=2, appraisers=2,
                                tolerance=10)
    got = grr_average_range(data, tolerance=10)
    assert got.grr == pytest.approx(expected.grr)
    assert got.pct_tolerance == pytest.approx(100 * 6 * got.grr / 10)
    assert got.ev == pytest.approx(((r_bar_a + r_bar_b) / 2) * 0.8862)


def test_unsupported_design():
    with pytest.raises(ValueError):
        grr_from_summary(1, 1, 1, parts=11, trials=3, appraisers=3)
