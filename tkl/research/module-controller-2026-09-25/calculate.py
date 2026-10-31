#!/usr/bin/env python3
"""Compare removable v7.4 quote lines; this does not quote a new PCB."""
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "tkl7.4"
QUOTE = SOURCE / "manufacturing/quote-v7.4-2026-09-25"
groups = json.loads((QUOTE / "bom-matches.json").read_text())
record = json.loads((QUOTE / "record.json").read_text())
count = record["assembled_quantity"]
assert count == 5 and len(groups) == 31 and all(g["selected"] for g in groups)
fee = Decimal("1.50")  # 31 feeders = $46.50 in the saved Standard quote.

controller = {"U1", "J4", "X1", "X2"}
controller.update(f"L{i}" for i in range(1, 6))
controller.update(f"C{i}" for i in range(1, 21) if i not in (10, 13))
module_usb_charger = controller | {
    "J3", "U2", "U3", "R11", "R12", "R13", "R14", "J5",
    "C21", "C22", "C23", "C24", "C25",
}

def money(value):
    return str(value.quantize(Decimal("0.01")))

results = []
rows = []
for name, removed in (
    ("controller_only_keep_carrier_charger_and_usb", controller),
    ("controller_plus_module_usb_and_charger_conditional", module_usb_charger),
):
    whole = []
    partial = []
    for group in groups:
        cells = group["cells"]
        refs = set(cells[0].split(","))
        cost = Decimal(cells[7].removeprefix("$"))
        if refs <= removed:
            whole.append({"references": cells[0], "quoted_parts_usd": str(cost)})
            rows.append([name, cells[0], cells[1], str(cost), str(fee)])
        elif refs & removed:
            partial.append({
                "removed_references": sorted(refs & removed),
                "retained_references": sorted(refs - removed),
                "unchanged_group_cost_usd": str(cost),
                "credited_saving_usd": "0",
            })
    parts = sum((Decimal(g["quoted_parts_usd"]) for g in whole), Decimal(0))
    feeders = fee * len(whole)
    gross = parts + feeders
    results.append({
        "scenario": name,
        "whole_groups_removed": len(whole),
        "groups_remaining": len(groups) - len(whole),
        "removed_parts_usd": money(parts),
        "removed_feeder_fees_usd": money(feeders),
        "gross_removed_cost_usd": money(gross),
        "net_saving_after_five_4_dollar_clones_usd": money(gross - count * Decimal(4)),
        "net_saving_after_five_25_dollar_genuine_modules_usd": money(gross - count * Decimal(25)),
        "whole_group_details": whole,
        "partial_groups_no_savings_credited": partial,
    })

output = {
    "status": "line-item feasibility comparison, not a new JLCPCB quote",
    "date": "2026-09-25",
    "quantity": count,
    "baseline_revision": "v7.4",
    "baseline_delivered_estimate_usd": str(record["total_including_shipping_and_rail_removal_usd"]),
    "module_prices": "User-supplied assumptions: $4 clone or $25 genuine, excluding separate freight/tax",
    "assumptions": [
        "User installs modules; no JLC module procurement or assembly cost is assumed.",
        "Only complete BOM group removal is credited, preserving quoted attrition prices.",
        "Remaining group quantities/attrition and feeder charges need a new JLC quote.",
        "No credit for PCB, X-ray, placement, freight, USB hand-solder or other fees.",
        "No allowance for new carrier interface, power integration or mounting hardware.",
        "Module charger scenario is conditional on battery/thermal/charge-safety validation.",
        "Retaining the carrier charger requires an engineered power/USB interface, not parallel chargers.",
    ],
    "inputs_sha256": {
        str(path.relative_to(SOURCE)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [QUOTE / "bom-matches.json", QUOTE / "record.json", SOURCE / "reference/firmware-pins.json"]
    },
    "scenarios": results,
}
(HERE / "cost-comparison.json").write_text(json.dumps(output, indent=2) + "\n")
with (HERE / "removed-quote-groups.csv").open("w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["Scenario", "References", "Part", "FiveBoardQuotedPartCostUSD", "FeederFeeUSD"])
    writer.writerows(rows)

# Official nice!nano v2 pinout; exact clone routing must be checked separately.
edge = {
    "P0.06", "P0.08", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04",
    "P1.06", "P0.09", "P0.10", "P1.11", "P1.13", "P1.15", "P0.02", "P0.29", "P0.31",
}
aux = {"P1.01", "P1.02", "P1.07"}
source_pins = json.loads((SOURCE / "reference/firmware-pins.json").read_text())
pin_rows = []
for signal, data in source_pins.items():
    old = data["gpio"].split("/")[-1].split("_")[0]
    new = {"ROW1": "P0.09", "ROW2": "P0.10"}.get(signal, old)
    assert new in edge | aux
    pin_rows.append([signal, old, new, "auxiliary solder pad" if new in aux else "edge pin"])
assert len(pin_rows) == len({row[2] for row in pin_rows}) == 21
with (HERE / "candidate-pinmap.csv").open("w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["Signal", "CurrentV74GPIO", "CandidateNiceNanoV2GPIO", "Connection"])
    writer.writerows(pin_rows)

fit = json.loads((SOURCE / "case/fit-report.json").read_text())
config = json.loads((SOURCE / "case/fit-config.json").read_text())
clearances = {
    str(y): round(fit["pcb_underside_front_origin_z"] + y * math.sin(math.radians(fit["tilt_degrees"])) - 1.2, 3)
    for y in (96, 120)
}
feasibility = {
    "pins": {"matrix": 20, "lighting": 1, "official_module_available": 21,
             "clone_pin_mapping_verified": False,
             "note": "User confirms extra pads; prior question misnamed two of them. Correct official pads: P1.01/P1.02/P1.07."},
    "case": {
        "external_dimensions_change_proposed": False,
        "front_rear_lips_mm": [fit["front_lip"], fit["rear_lip"]],
        "nominal_vertical_floor_to_pcb_clearance_by_board_y_mm": clearances,
        "floor_thickness_mm": 1.2,
        "battery_reserve_x_end_case_mm": config["battery"]["origin_xy_case_mm"][0] + config["battery"]["reserved_dimensions_mm"][0],
        "candidate_region": "underside at rear right, outside battery reserve",
        "module_fit_validated": False,
        "note": "Plane-to-floor space only, before switch tails, carrier parts, insulation, mounts and antenna clearance. No module STEP/mesh or collision test yet.",
    },
}
(HERE / "feasibility.json").write_text(json.dumps(feasibility, indent=2) + "\n")
for result in results:
    print(result["scenario"], result["whole_groups_removed"], "groups; clone net saving $" + result["net_saving_after_five_4_dollar_clones_usd"])
