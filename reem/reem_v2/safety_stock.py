import csv
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))

DEMAND = os.path.join(BASE, "demand_model.csv")
SUPPLIERS = os.path.join(BASE, "supplier_intelligence.csv")
OUTPUT = os.path.join(BASE, "safety_stock_intelligence.csv")

demand = {}

with open(DEMAND, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        demand[r["DrugID"]] = {
            "mae": float(r["SelectedMAE"]),
            "forecast": float(r["SelectedForecast"])
        }

lead_times = []

with open(SUPPLIERS, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        lead_times.append(float(r["AverageLeadTimeDays"]))

if lead_times:
    average_lead_time = sum(lead_times) / len(lead_times)
else:
    average_lead_time = 7.0

rows = []

for drug in sorted(demand):

    mae = demand[drug]["mae"]
    forecast = demand[drug]["forecast"]

    safety_stock = 1.65 * mae * math.sqrt(average_lead_time)

    rows.append({
        "DrugID": drug,
        "ForecastDailyDemand": round(forecast, 4),
        "DemandUncertaintyMAE": round(mae, 4),
        "LeadTimeDays": round(average_lead_time, 2),
        "ServiceFactor": 1.65,
        "SafetyStock": round(safety_stock, 2),
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    fields = [
        "DrugID",
        "ForecastDailyDemand",
        "DemandUncertaintyMAE",
        "LeadTimeDays",
        "ServiceFactor",
        "SafetyStock",
        "DataSource",
        "DataStatus",
        "OperationalUse"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

values = [r["SafetyStock"] for r in rows]

print("=" * 60)
print("REEM V2 — SAFETY STOCK INTELLIGENCE")
print("=" * 60)
print()
print("Medicines analysed :", len(rows))
print("Service factor     : 1.65")
print("Average lead time  :", round(average_lead_time, 2), "days")
print()
print("Safety stock:")
print("  Minimum          :", round(min(values), 2))
print("  Maximum          :", round(max(values), 2))
print("  Mean             :", round(sum(values) / len(values), 2))
print()
print("Output:")
print("  safety_stock_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
