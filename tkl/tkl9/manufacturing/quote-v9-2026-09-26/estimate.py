"""Historical pre-login estimate, superseded by the live record.json files.

Public catalog prices were fetched from JLC on 2026-09-26. Purchase allowances
carry forward the absolute overage in the 2026-09-25 v7.4 quote, not a promise
about the quantities JLC will choose for v9. No network or account access.
"""
import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
MFG = HERE.parent
TKL = MFG.parents[1]
public = {p["code"]: p for p in json.loads((HERE / "public-parts.json").read_text())}
old = json.loads((TKL / "tkl7.4/manufacturing/quote-v7.4-2026-09-25/bom-matches.json").read_text())


def money(value):
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


parts = []
for row in csv.DictReader((MFG / "jlcpcb-bom.csv").open()):
    code = row["LCSC Part #"]
    saved = next(x["cells"] for x in old if code in x["cells"][3].split())
    prior_installed = len(saved[0].split(",")) * 5
    allowance = max(0, int(saved[4]) - prior_installed)
    installed = int(row["Quantity"]) * 5
    purchased = installed + allowance
    rows = public[code]["rows"]
    tier = next(x for x in rows if "productPrice" in x and x["startNumber"] <= purchased
                and (x["endNumber"] == -1 or purchased <= x["endNumber"]))
    cost = Decimal(str(tier["productPrice"])) * purchased
    parts.append({"code": code, "mpn": row["Comment"], "installed": installed,
                  "assumed_purchased": purchased, "unit_price": tier["productPrice"],
                  "cost": float(cost), "source": public[code]["url"]})

# Rates: https://jlcpcb.com/help/article/pcb-assembly-price (2026-09-26).
# 202 SMT pads/board counted from the exact carrier PCB, including switch tabs.
fees = {
    "standard_single_side_setup": 25.56,
    "stencil": 8.21,
    "seven_group_feeder_loading": 7 * 1.53,
    "smt_202_joints_times_5": money(202 * 5 * 0.0016),
    "hand_solder_order_labor": 3.58,
    "j1_manual_2_joints_times_5": money(2 * 5 * 0.0164),
    "placement_confirmation": 0.45,
    "packaging": money(0.50 + 0.00003 * (350.76 * 139.19 / 100)),
    # Exact depanel charge pending v9 quote; prior v7.4 five-board quote.
    "rail_removal_prior_quote_allowance": 3.31,
}
components = money(sum(Decimal(str(p["cost"])) for p in parts))
assembly = money(sum(Decimal(str(v)) for v in fees.values()))
fabrication = 28.55  # Live configured v9 PCB-only price, including rails/review.
freight = 45.37  # Prior v7.4 DHL DDP US estimate; NOT a fresh v9 shipping quote.
base = money(Decimal(str(components)) + Decimal(str(assembly))
             + Decimal(str(fabrication)) + Decimal(str(freight)))
record = {
    "date": "2026-09-26", "currency": "USD", "pcb_quantity": 5,
    "assembly_quantity": 5, "status": "partial_live_fabrication_plus_assembly_estimate",
    "live_v9_matched_assembly_quote_completed": False,
    "live_fabrication": {"price": fabrication, "engineering": 4,
        "board": 23.50, "production_file_confirmation": 1.05,
        "configured_size_with_rails_mm": [350.76, 139.19],
        "finished_size_mm": [350.76, 129.19], "layers": 2, "thickness_mm": 1.6,
        "finish": "OSP", "copper_oz": 1, "assembly_side": "bottom",
        "via_drill_mm": 0.3, "via_covering": "tented", "via_plating": "not specified",
        "economic_disabled_for_this_configuration": True},
    "components": parts, "component_estimate": components,
    "assembly_fee_estimate": fees, "assembly_fees_total": assembly,
    "shipping_allowance_from_v7_4_quote": freight,
    "estimated_batch_delivered_before_tax": base,
    "conditional_fixture_allowance": 16.42,
    "estimated_batch_with_fixture_before_tax": money(base + 16.42),
    "customer_installed_modules_separate": {"quantity": 5,
        "user_reported_unit_price": 4, "additional_cost_if_purchased": 20},
    "excludes": ["tax", "unquoted engineering/manual handling charges",
        "case", "battery", "keycaps", "key switches", "stabilizers", "module mounting hardware"],
    "next_step": "Sign in to isolated quote browser, upload BOM/CPL, match parts, quote shipping.",
    "files": {n: hashlib.sha256((MFG / n).read_bytes()).hexdigest()
              for n in ["tkl-v9-gerbers.zip", "jlcpcb-bom.csv", "jlcpcb-cpl.csv"]},
}
(HERE / "estimate.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({k: record[k] for k in ["component_estimate", "assembly_fees_total",
    "estimated_batch_delivered_before_tax", "estimated_batch_with_fixture_before_tax"]}, indent=2))
