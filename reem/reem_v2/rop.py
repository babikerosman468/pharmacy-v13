import csv
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

DEMAND = os.path.join(BASE, "demand_model.csv")
SUPPLIERS = os.path.join(BASE, "supplier_intelligence.csv")
INVENTORY = os.path.join(BASE, "inventory_intelligence.csv")
OUTPUT = os.path.join(BASE, "rop_intelligence.csv")

demand = {}

with open(DEMAND, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        demand[r["DrugID"]] = {
            "forecast": float(r["SelectedForecast"]),
            "mae": float(r["SelectedMAE"])
        }

lead_times = []

with open(SUPPLIERS, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        lead_times.append(float(r["AverageLeadTimeDays"]))

if lead_times:
    global_lead = sum(lead_times) / len(lead_times)
else:
    global_lead = 7.0

stock = {}

with open(INVENTORY, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        stock[r["DrugID"]] = float(r["CurrentStock"])

rows = []

for drug in sorted(demand):

    forecast = demand[drug]["forecast"]
    mae = demand[drug]["mae"]
    current_stock = stock.get(drug, 0.0)

    lead_time = global_lead

    safety_stock = 1.65 * mae * math.sqrt(lead_time)

    lead_time_demand = forecast * lead_time

    reorder_point = lead_time_demand + safety_stock

    if current_stock <= 0:
        decision = "STOCKOUT"
    elif current_stock <= reorder_point:
        decision = "REORDER"
    elif current_stock <= reorder_point * 1.5:
        decision = "WATCH"
    else:
        decision = "ADEQUATE"

    rows.append({
        "DrugID": drug,
        "ForecastDailyDemand": round(forecast, 4),
        "LeadTimeDays": round(lead_time, 2),
        "LeadTimeDemand": round(lead_time_demand, 2),
        "SafetyStock": round(safety_stock, 2),
        "ReorderPoint": round(reorder_point, 2),
        "CurrentStock": round(current_stock, 2),
        "Decision": decision,
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    fields = [
        "DrugID",
        "ForecastDailyDemand",
        "LeadTimeDays",
        "LeadTimeDemand",
        "SafetyStock",
        "ReorderPoint",
        "CurrentStock",
        "Decision",
        "DataSource",
        "DataStatus",
        "OperationalUse"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

counts = {}

for r in rows:
    decision = r["Decision"]
    counts[decision] = counts.get(decision, 0) + 1

print("=" * 60)
print("REEM V2 — REORDER POINT INTELLIGENCE")
print("=" * 60)
print()
print("Medicines analysed :", len(rows))
print("Global lead time   :", round(global_lead, 2), "days")
print()
print("Decisions:")
for decision in ["STOCKOUT", "REORDER", "WATCH", "ADEQUATE"]:
    print("  %-10s : %d" % (decision, counts.get(decision, 0)))
print()
print("Output:")
print("  rop_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
