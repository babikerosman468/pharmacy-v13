import csv
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

INPUT = os.path.join(SCHEMA, "inventory_batches.csv")
OUTPUT = os.path.join(BASE, "expiry_intelligence.csv")

TODAY = datetime.now().date()

rows = []

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for r in reader:
        try:
            expiry = datetime.strptime(
                r["ExpiryDate"], "%Y-%m-%d"
            ).date()
        except Exception:
            continue

        try:
            quantity = float(r["RemainingQuantity"])
        except Exception:
            quantity = 0.0

        days_to_expiry = (expiry - TODAY).days

        if quantity <= 0:
            risk = "NO_STOCK"
        elif days_to_expiry < 0:
            risk = "EXPIRED"
        elif days_to_expiry <= 30:
            risk = "CRITICAL"
        elif days_to_expiry <= 90:
            risk = "HIGH"
        elif days_to_expiry <= 180:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        rows.append({
            "BatchID": r["BatchID"],
            "DrugID": r["DrugID"],
            "Quantity": quantity,
            "ExpiryDate": r["ExpiryDate"],
            "DaysToExpiry": days_to_expiry,
            "ExpiryRisk": risk,
            "DataSource": r["DataSource"],
            "DataStatus": r["DataStatus"],
            "OperationalUse": "PROHIBITED"
        })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    fields = [
        "BatchID",
        "DrugID",
        "Quantity",
        "ExpiryDate",
        "DaysToExpiry",
        "ExpiryRisk",
        "DataSource",
        "DataStatus",
        "OperationalUse"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

counts = {}

for r in rows:
    risk = r["ExpiryRisk"]
    counts[risk] = counts.get(risk, 0) + 1

print("=" * 60)
print("REEM V2 — EXPIRY RISK INTELLIGENCE")
print("=" * 60)
print()
print("Batches analysed :", len(rows))
print()
print("Expiry risk:")
for risk in ["EXPIRED", "CRITICAL", "HIGH", "MEDIUM", "LOW", "NO_STOCK"]:
    print("  %-10s : %d" % (risk, counts.get(risk, 0)))
print()
print("Output:")
print("  expiry_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
