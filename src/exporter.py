"""Export dilution plans to XLSX / CSV / PDF-ready formats."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from .planner import DilutionPlan

logger = logging.getLogger(__name__)


def export_plan(plan: DilutionPlan, output_path: Path) -> None:
    """Export dilution plan based on file extension."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()

    if suffix == ".csv":
        _export_csv(plan, output_path)
    else:
        _export_xlsx(plan, output_path)
        csv_path = output_path.with_suffix(".csv")
        _export_csv(plan, csv_path)

    logger.info("Dilution plan exported to %s", output_path)


def _export_csv(plan: DilutionPlan, path: Path) -> None:
    """Export tube-by-tube plan to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "Tube", "Label", "Source", "Transfer_ul",
            "Diluent_ul", "Final_Volume_ul", "Concentration",
            "Dilution_Factor", "Cumulative_Dilution",
        ])
        for t in plan.tubes:
            writer.writerow([
                t.tube_number, t.label, t.source,
                t.transfer_volume_ul, t.diluent_volume_ul,
                t.final_volume_ul,
                f"{t.concentration} {plan.starting_unit}",
                t.dilution_factor, t.cumulative_dilution,
            ])


def _export_xlsx(plan: DilutionPlan, path: Path) -> None:
    """Export to multi-sheet XLSX."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    hdr = Font(bold=True)

    # Summary
    ws = wb.active
    ws.title = "Summary"
    summary = [
        ("Field", "Value"),
        ("Sample Name", plan.sample_name),
        ("Starting Concentration", f"{plan.starting_concentration} {plan.starting_unit}"),
        ("Final Volume per Tube", f"{plan.final_volume_ul} µL"),
        ("Number of Tubes", len(plan.tubes)),
        ("Total Stock Needed", f"{plan.total_stock_needed_ul} µL"),
        ("Warnings", len(plan.warnings)),
    ]
    for row in summary:
        ws.append(row)
    for c in ws[1]:
        c.font = hdr

    # Dilution Plan
    ws2 = wb.create_sheet("Dilution Plan")
    headers = ["Tube", "Label", "Source", "Transfer (µL)",
               "Diluent (µL)", "Final Volume (µL)",
               f"Concentration ({plan.starting_unit})",
               "Dilution Factor", "Cumulative Dilution"]
    ws2.append(headers)
    for c in ws2[1]:
        c.font = hdr
    for t in plan.tubes:
        ws2.append([
            t.tube_number, t.label, t.source,
            t.transfer_volume_ul, t.diluent_volume_ul, t.final_volume_ul,
            t.concentration, t.dilution_factor, t.cumulative_dilution,
        ])

    # Tube Labels
    ws3 = wb.create_sheet("Tube Labels")
    ws3.append(["Label", "Concentration", "Tube #"])
    for c in ws3[1]:
        c.font = hdr
    for t in plan.tubes:
        ws3.append([t.label, f"{t.concentration} {plan.starting_unit}", t.tube_number])

    # Warnings
    if plan.warnings:
        ws4 = wb.create_sheet("Warnings")
        ws4.append(["#", "Warning"])
        for c in ws4[1]:
            c.font = hdr
        for i, w in enumerate(plan.warnings, 1):
            ws4.append([i, w])

    # Methods
    ws5 = wb.create_sheet("Methods")
    methods = [
        ("Method", "Description"),
        ("C1V1 = C2V2", "Standard dilution formula"),
        ("V1 = C2 × V2 / C1", "Stock volume required"),
        ("DF = C1 / C2", "Dilution factor"),
        ("", ""),
        ("Disclaimer", "Verify the calculated plan against your laboratory SOP, "
                       "reagent compatibility, and pipetting constraints before use."),
        ("Source", "BioSyn Serial Dilution Planner v1.0.0 — https://biosyn-inc.com/"),
    ]
    for row in methods:
        ws5.append(row)

    wb.save(path)
