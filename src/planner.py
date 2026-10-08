"""
Serial Dilution Planner engine — generates step-by-step dilution plans.

All calculations are mathematical planning tools. Verify against lab SOP before use.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# Unit conversion to base unit (M for molar, g/L for mass)
MOLAR_UNITS = {"M": 1.0, "mM": 1e-3, "µM": 1e-6, "nM": 1e-9, "pM": 1e-12}
MASS_UNITS = {"g/L": 1.0, "mg/mL": 1.0, "µg/mL": 1e-3, "ng/mL": 1e-6}
VOLUME_UNITS = {"L": 1.0, "mL": 1e-3, "µL": 1e-6}


@dataclass
class TubePlan:
    """Dilution plan for a single tube."""
    tube_number: int
    label: str
    source: str
    transfer_volume_ul: float       # µL transferred from source
    diluent_volume_ul: float        # µL diluent added
    final_volume_ul: float          # final volume in tube
    concentration: float            # final concentration (in display unit)
    dilution_factor: float          # dilution fold from stock
    cumulative_dilution: float      # cumulative dilution from starting stock
    notes: str = ""


@dataclass
class DilutionPlan:
    """Complete serial dilution plan."""
    sample_name: str
    starting_concentration: float
    starting_unit: str
    target_concentrations: List[float] = field(default_factory=list)
    final_volume_ul: float = 0.0
    tubes: List[TubePlan] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_stock_needed_ul: float = 0.0


class DilutionPlanner:
    """Generate serial dilution plans from user inputs."""

    def __init__(
        self,
        min_transfer_ul: float = 2.0,
        dead_volume_ul: float = 0.0,
        excess_volume_pct: float = 0.0,
    ) -> None:
        self.min_transfer_ul = min_transfer_ul
        self.dead_volume_ul = dead_volume_ul
        self.excess_volume_pct = excess_volume_pct

    def plan_from_factors(
        self,
        start_conc: float,
        start_unit: str,
        dilution_factor: float,
        num_tubes: int,
        final_volume_ul: float,
        sample_name: str = "Sample",
    ) -> DilutionPlan:
        """
        Mode B: Plan a serial dilution with a fixed dilution factor.

        Args:
            start_conc: Starting (stock) concentration.
            start_unit: Unit of starting concentration.
            dilution_factor: e.g. 10 for 1:10 dilution.
            num_tubes: Number of dilution tubes.
            final_volume_ul: Final volume per tube (µL).
            sample_name: Sample name for tube labels.
        """
        tubes: List[TubePlan] = []
        warnings: List[str] = []
        transfer_ul = final_volume_ul / dilution_factor
        diluent_ul = final_volume_ul - transfer_ul

        for i in range(1, num_tubes + 1):
            cum_df = dilution_factor ** i
            conc = start_conc / cum_df
            source = "Stock" if i == 1 else f"Tube {i-1}"
            label = f"{sample_name}-T{i:02d}"

            # Safety checks
            if transfer_ul < self.min_transfer_ul:
                warnings.append(
                    f"Tube {i}: transfer volume {transfer_ul:.1f} µL is below "
                    f"minimum pipetting threshold ({self.min_transfer_ul} µL)."
                )

            if diluent_ul < 0:
                warnings.append(
                    f"Tube {i}: diluent volume would be negative. "
                    f"Dilution factor {dilution_factor} too large for {final_volume_ul} µL final volume."
                )

            tubes.append(TubePlan(
                tube_number=i,
                label=label,
                source=source,
                transfer_volume_ul=round(transfer_ul, 2),
                diluent_volume_ul=round(diluent_ul, 2),
                final_volume_ul=final_volume_ul,
                concentration=round(conc, 6),
                dilution_factor=dilution_factor,
                cumulative_dilution=cum_df,
            ))

        total_stock = tubes[0].transfer_volume_ul if tubes else 0
        return DilutionPlan(
            sample_name=sample_name,
            starting_concentration=start_conc,
            starting_unit=start_unit,
            final_volume_ul=final_volume_ul,
            tubes=tubes,
            warnings=warnings,
            total_stock_needed_ul=total_stock,
        )

    def plan_from_targets(
        self,
        start_conc: float,
        start_unit: str,
        targets: List[float],
        final_volume_ul: float,
        sample_name: str = "Sample",
    ) -> DilutionPlan:
        """
        Mode C: Plan dilution to reach user-specified target concentrations.

        For each target, compute V1 = C2 × V2 / C1.
        """
        tubes: List[TubePlan] = []
        warnings: List[str] = []

        sorted_targets = sorted(targets, reverse=True)
        prev_conc = start_conc

        for i, target in enumerate(sorted_targets, start=1):
            # C1V1 = C2V2 → V1 = C2*V2/C1
            v1_ul = (target * final_volume_ul) / prev_conc if prev_conc > 0 else 0
            diluent_ul = final_volume_ul - v1_ul
            df = prev_conc / target if target > 0 else float("inf")

            source = "Stock" if i == 1 else f"Tube {i-1}"
            label = f"{sample_name}-T{i:02d}"

            if v1_ul < self.min_transfer_ul:
                warnings.append(
                    f"Tube {i}: transfer volume {v1_ul:.2f} µL below minimum "
                    f"({self.min_transfer_ul} µL). Consider a two-step dilution."
                )

            if target > start_conc:
                warnings.append(
                    f"Tube {i}: target {target} > starting concentration {start_conc}. "
                    f"Cannot dilute to a higher concentration."
                )

            tubes.append(TubePlan(
                tube_number=i,
                label=label,
                source=source,
                transfer_volume_ul=round(v1_ul, 2),
                diluent_volume_ul=round(diluent_ul, 2),
                final_volume_ul=final_volume_ul,
                concentration=round(target, 6),
                dilution_factor=round(df, 2),
                cumulative_dilution=round(start_conc / target, 2) if target > 0 else 0,
            ))
            prev_conc = target

        return DilutionPlan(
            sample_name=sample_name,
            starting_concentration=start_conc,
            starting_unit=start_unit,
            target_concentrations=sorted_targets,
            final_volume_ul=final_volume_ul,
            tubes=tubes,
            warnings=warnings,
            total_stock_needed_ul=tubes[0].transfer_volume_ul if tubes else 0,
        )

    @staticmethod
    def reverse_calculate(
        target_conc: float, final_volume_ul: float, stock_conc: float,
    ) -> Dict[str, float]:
        """
        Reverse calculation: given target concentration and final volume,
        compute required stock volume and diluent volume.

        Returns: {"stock_ul": ..., "diluent_ul": ...}
        """
        stock_ul = (target_conc * final_volume_ul) / stock_conc if stock_conc > 0 else 0
        diluent_ul = final_volume_ul - stock_ul
        return {
            "stock_ul": round(stock_ul, 2),
            "diluent_ul": round(diluent_ul, 2),
        }
