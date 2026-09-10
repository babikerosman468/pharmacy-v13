import csv
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))

DEMAND = os.path.join(BASE, "demand_model.csv")
MEDICINES = os.path.join(BASE, "schema", "medicines.csv")
OUTPUT = os.path.join(BASE, "eoq_intelligence.csv")

demand = {}

with open(DEMAND, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        demand[r["DrugID"]] = {
            "forecast": float(r["SelectedForecast"])
        }

medicines = {}

with open(MEDICINES, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        medicines[r["DrugID"]] = {
            "unit_cost": float(r["UnitCost"])
        }

rows = []

for drug in sorted(demand):

    annual_demand = demand[drug]["forecast"] * 365
    unit_cost = medicines.get(drug, {}).get("unit_cost", 0.0)

    ordering_cost = 25.0
    holding_rate = 0.25
    holding_cost = unit_cost * holding_rate

    if annual_demand > 0 and holding_cost > 0:

        eoq = math.sqrt(
            (2 * annual_demand * ordering_cost) /
            holding_cost
        )

    else:

        eoq = 0.0

    rows.append({
        "DrugID": drug,
        "AnnualDemand": round(annual_demand, 2),
        "UnitCost": round(unit_cost, 4),
        "OrderingCost": ordering_cost,
        "HoldingRate": holding_rate,
        "HoldingCostPerUnit": round(holding_cost, 4),
        "EOQ": round(eoq, 2),
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

fields = [
    "DrugID",
    "AnnualDemand",
    "UnitCost",
    "OrderingCost",
    "HoldingRate",
    "HoldingCostPerUnit",
    "EOQ",
    "DataSource",
    "DataStatus",
    "OperationalUse"
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

values = [r["EOQ"] for r in rows if r["EOQ"] > 0]

print("=" * 60)
print("REEM V2 — EOQ INTELLIGENCE")
print("=" * 60)
print()
print("Medicines analysed :", len(rows))
print("Ordering cost      : 25.00")
print("Holding rate       : 25% of unit cost")
print()

if values:

    print("EOQ:")
    print("  Minimum          :", round(min(values), 2))
    print("  Maximum          :", round(max(values), 2))
    print("  Mean             :", round(sum(values) / len(values), 2))

print()
print("Output:")
print("  eoq_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
