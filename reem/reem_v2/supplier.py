import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

PURCHASES = os.path.join(SCHEMA, "purchases.csv")
DELIVERIES = os.path.join(SCHEMA, "deliveries.csv")
OUTPUT = os.path.join(BASE, "supplier_intelligence.csv")

suppliers = {}

with open(PURCHASES, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        supplier = r["SupplierID"]

        if supplier not in suppliers:
            suppliers[supplier] = {
                "orders": 0,
                "ordered_units": 0.0,
                "cost": 0.0
            }

        suppliers[supplier]["orders"] += 1
        suppliers[supplier]["ordered_units"] += float(r["OrderQuantity"])
        suppliers[supplier]["cost"] += float(r["TotalCost"])

delivery_count = {}
on_time_count = {}
lead_time_total = {}

with open(DELIVERIES, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):

        supplier = r["SupplierID"]

        delivery_count[supplier] = delivery_count.get(supplier, 0) + 1

        if r["OnTime"].strip().upper() == "TRUE":
            on_time_count[supplier] = on_time_count.get(supplier, 0) + 1

        lead_time_total[supplier] = (
            lead_time_total.get(supplier, 0.0)
            + float(r["LeadTimeDays"])
        )

rows = []

for supplier in sorted(suppliers):

    orders = suppliers[supplier]["orders"]
    units = suppliers[supplier]["ordered_units"]
    cost = suppliers[supplier]["cost"]

    deliveries = delivery_count.get(supplier, 0)
    on_time = on_time_count.get(supplier, 0)
    lead_total = lead_time_total.get(supplier, 0.0)

    if deliveries > 0:
        on_time_rate = on_time / deliveries * 100
        avg_lead_time = lead_total / deliveries
    else:
        on_time_rate = 0.0
        avg_lead_time = 0.0

    if on_time_rate >= 90:
        reliability = "HIGH"
    elif on_time_rate >= 75:
        reliability = "MEDIUM"
    else:
        reliability = "LOW"

    rows.append({
        "SupplierID": supplier,
        "Orders": orders,
        "Deliveries": deliveries,
        "OrderedUnits": round(units, 2),
        "ProcurementCost": round(cost, 2),
        "OnTimeDeliveries": on_time,
        "OnTimeRatePercent": round(on_time_rate, 2),
        "AverageLeadTimeDays": round(avg_lead_time, 2),
        "SupplierReliability": reliability,
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    fields = [
        "SupplierID",
        "Orders",
        "Deliveries",
        "OrderedUnits",
        "ProcurementCost",
        "OnTimeDeliveries",
        "OnTimeRatePercent",
        "AverageLeadTimeDays",
        "SupplierReliability",
        "DataSource",
        "DataStatus",
        "OperationalUse"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

counts = {}

for r in rows:
    reliability = r["SupplierReliability"]
    counts[reliability] = counts.get(reliability, 0) + 1

print("=" * 60)
print("REEM V2 — SUPPLIER INTELLIGENCE")
print("=" * 60)
print()
print("Suppliers analysed :", len(rows))
print()
print("Reliability:")
for level in ["HIGH", "MEDIUM", "LOW"]:
    print("  %-10s : %d" % (level, counts.get(level, 0)))
print()
print("Output:")
print("  supplier_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
