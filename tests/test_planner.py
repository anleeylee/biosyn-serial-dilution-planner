"""Tests for BioSyn Serial Dilution Planner."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from planner import DilutionPlanner


def test_fixed_factor():
    p = DilutionPlanner()
    plan = p.plan_from_factors(
        start_conc=1000, start_unit="µg/mL",
        dilution_factor=10, num_tubes=5, final_volume_ul=1000,
    )
    assert len(plan.tubes) == 5
    assert plan.tubes[0].transfer_volume_ul == 100.0
    assert plan.tubes[0].concentration == 100.0
    assert plan.tubes[4].concentration == 0.01


def test_targets():
    p = DilutionPlanner()
    plan = p.plan_from_targets(
        start_conc=1000, start_unit="µg/mL",
        targets=[100, 10, 1], final_volume_ul=500,
    )
    assert len(plan.tubes) == 3
    assert plan.tubes[0].concentration == 100


def test_small_transfer_warning():
    p = DilutionPlanner(min_transfer_ul=50.0)
    plan = p.plan_from_factors(
        start_conc=1000, start_unit="µg/mL",
        dilution_factor=100, num_tubes=3, final_volume_ul=1000,
    )
    assert len(plan.warnings) > 0


def test_reverse_calc():
    result = DilutionPlanner.reverse_calculate(10, 500, 100)
    assert result["stock_ul"] == 50.0
    assert result["diluent_ul"] == 450.0


if __name__ == "__main__":
    test_fixed_factor(); test_targets()
    test_small_transfer_warning(); test_reverse_calc()
    print("All tests passed!")
