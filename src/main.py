"""
CLI entry point for BioSyn Serial Dilution Planner.

Usage:
    python -m src.main factor --start 1000 --factor 10 --tubes 5 --volume 1000
    python -m src.main targets --start 1000 --targets 100,10,1,0.1 --volume 500
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import List

from .planner import DilutionPlanner, DilutionPlan
from .exporter import export_plan

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="biosyn-dilution",
        description="BioSyn Serial Dilution Planner — lab dilution calculation.",
        epilog="Built by BioSyn Inc. — https://biosyn-inc.com/",
    )
    sub = parser.add_subparsers(dest="mode")

    # Mode B: fixed factor
    p_factor = sub.add_parser("factor", help="Serial dilution with fixed factor")
    p_factor.add_argument("--start", type=float, required=True, help="Starting concentration")
    p_factor.add_argument("--unit", default="µg/mL", help="Concentration unit")
    p_factor.add_argument("--factor", type=float, required=True, help="Dilution factor (e.g. 10 for 1:10)")
    p_factor.add_argument("--tubes", type=int, required=True, help="Number of tubes")
    p_factor.add_argument("--volume", type=float, required=True, help="Final volume per tube (µL)")
    p_factor.add_argument("--name", default="Sample", help="Sample name for labels")
    p_factor.add_argument("--output", "-o", type=Path, default=Path("dilution_plan.xlsx"))
    p_factor.add_argument("--min-transfer", type=float, default=2.0, help="Minimum pipetting volume (µL)")

    # Mode C: user targets
    p_target = sub.add_parser("targets", help="Dilution to user-specified targets")
    p_target.add_argument("--start", type=float, required=True)
    p_target.add_argument("--unit", default="µg/mL")
    p_target.add_argument("--targets", type=str, required=True,
                          help="Comma-separated target concentrations, e.g. 100,10,1,0.1")
    p_target.add_argument("--volume", type=float, required=True, help="Final volume per tube (µL)")
    p_target.add_argument("--name", default="Sample")
    p_target.add_argument("--output", "-o", type=Path, default=Path("dilution_plan.xlsx"))
    p_target.add_argument("--min-transfer", type=float, default=2.0)

    args = parser.parse_args(argv)
    setup_logging()

    planner = DilutionPlanner(min_transfer_ul=args.min_transfer)

    try:
        if args.mode == "factor":
            plan = planner.plan_from_factors(
                start_conc=args.start,
                start_unit=args.unit,
                dilution_factor=args.factor,
                num_tubes=args.tubes,
                final_volume_ul=args.volume,
                sample_name=args.name,
            )
        elif args.mode == "targets":
            targets = [float(t.strip()) for t in args.targets.split(",")]
            plan = planner.plan_from_targets(
                start_conc=args.start,
                start_unit=args.unit,
                targets=targets,
                final_volume_ul=args.volume,
                sample_name=args.name,
            )
        else:
            parser.print_help()
            return 1

        export_plan(plan, args.output)
        print(f"\nDilution plan generated: {len(plan.tubes)} tubes")
        for t in plan.tubes:
            print(f"  {t.label}: transfer {t.transfer_volume_ul} µL + "
                  f"diluent {t.diluent_volume_ul} µL → {t.concentration} {plan.starting_unit}")
        if plan.warnings:
            print("\nWarnings:")
            for w in plan.warnings:
                print(f"  ⚠ {w}")
        print(f"\nResults saved to: {args.output.resolve()}")
        print("\n⚠ Verify this plan against your lab SOP before use.")
        return 0
    except Exception as exc:
        logger.error("Error: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
