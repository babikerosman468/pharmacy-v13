import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

STOCK_FILE = os.path.join(SCHEMA, "inventory_batches.csv")
FORECAST_FILE = os.path.join(BASE, "demand_model.csv")
OUTPUT = os.path.join(BASE, "stock_coverage.csv")

stock = {}

with open(STOCK_FILE, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        drug = r["DrugID"]
        qty = float(r["RemainingQuantity"])
        stock[drug] = stock.get(drug, 0.0) + qty

forecast = {}

with open(FORECAST_FILE, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        forecast[r["DrugID"]] = float(r["SelectedForecast"])

rows = []

for drug in sorted(forecast):

    current_stock = stock.get(drug, 0.0)
    daily_demand = forecast[drug]

    if daily_demand > 0:
        coverage_days = current_stock / daily_demand
    else:
        coverage_days = 999999.0

    if current_stock <= 0:
        status = "STOCKOUT"
    elif coverage_days <= 7:
        status = "CRITICAL"
    elif coverage_days <= 30:
        status = "LOW"
    elif coverage_days <= 90:
        status = "ADEQUATE"
    else:
        status = "HIGH"

    rows.append({
        "DrugID": drug,
        "ForecastDailyDemand": round(daily_demand, 4),
        "CurrentStock": round(current_stock, 2),
        "CoverageDays": round(coverage_days, 2),
        "CoverageStatus": status,
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    fields = [
        "DrugID",
        "ForecastDailyDemand",
        "CurrentStock",
        "CoverageDays",
        "CoverageStatus",
        "DataSource",
        "DataStatus",
        "OperationalUse"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

counts = {}

for r in rows:
    status = r["CoverageStatus"]
    counts[status] = counts.get(status, 0) + 1

print("=" * 60)
print("REEM V2 — STOCK COVERAGE INTELLIGENCE")
print("=" * 60)
print()
print("Medicines analysed :", len(rows))
print()
print("Coverage status:")
for status in ["STOCKOUT", "CRITICAL", "LOW", "ADEQUATE", "HIGH"]:
    print("  %-10s : %d" % (status, counts.get(status, 0)))
print()
print("Output:")
print("  stock_coverage.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
