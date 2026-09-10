import csv
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

def number(value):
    try:
        return float(value)
    except:
        return 0.0

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

print("=" * 60)
print("REEM V2 — ABC INVENTORY INTELLIGENCE")
print("=" * 60)

medicines = read_csv(
    os.path.join(SCHEMA, "medicines.csv")
)

sales = read_csv(
    os.path.join(SCHEMA, "sales.csv")
)

medicine_map = {}

for row in medicines:
    medicine_map[row["DrugID"]] = row

sales_by_drug = {}
dates = []

for row in sales:
    drug_id = row.get("DrugID", "")
    quantity = number(row.get("Quantity"))
    timestamp = row.get("Timestamp", "")

    if drug_id:
        sales_by_drug[drug_id] = (
            sales_by_drug.get(drug_id, 0.0)
            + quantity
        )

    if timestamp:
        dates.append(timestamp[:10])

if not dates:
    print("ERROR: No sales dates found.")
    raise SystemExit(1)

start_date = datetime.strptime(
    min(dates), "%Y-%m-%d"
)

end_date = datetime.strptime(
    max(dates), "%Y-%m-%d"
)

observation_days = (
    end_date - start_date
).days + 1

if observation_days <= 0:
    observation_days = 1

results = []

for drug_id, medicine in medicine_map.items():

    quantity = sales_by_drug.get(drug_id, 0.0)

    unit_cost = number(
        medicine.get("UnitCost")
    )

    consumption_value = (
        quantity * unit_cost
    )

    annual_quantity = (
        quantity / observation_days
    ) * 365.0

    annual_consumption_value = (
        annual_quantity * unit_cost
    )

    results.append({
        "DrugID": drug_id,
        "GenericName": medicine.get(
            "GenericName", ""
        ),
        "UnitCost": round(unit_cost, 2),
        "ObservedQuantity": round(
            quantity, 2
        ),
        "ObservationDays": observation_days,
        "AnnualizedQuantity": round(
            annual_quantity, 2
        ),
        "ObservedConsumptionValue": round(
            consumption_value, 2
        ),
        "AnnualizedConsumptionValue": round(
            annual_consumption_value, 2
        ),
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

results.sort(
    key=lambda x: x["AnnualizedConsumptionValue"],
    reverse=True
)

total_value = sum(
    r["AnnualizedConsumptionValue"]
    for r in results
)

cumulative_value = 0.0

for r in results:

    value = r["AnnualizedConsumptionValue"]

    cumulative_value += value

    if total_value > 0:
        cumulative_percent = (
            cumulative_value / total_value
        ) * 100.0
    else:
        cumulative_percent = 0.0

    if cumulative_percent <= 80.0:
        abc_class = "A"
    elif cumulative_percent <= 95.0:
        abc_class = "B"
    else:
        abc_class = "C"

    r["ConsumptionValuePercent"] = round(
        (value / total_value * 100.0)
        if total_value > 0 else 0.0,
        2
    )

    r["CumulativeValuePercent"] = round(
        cumulative_percent,
        2
    )

    r["ABCClass"] = abc_class

    if abc_class == "A":
        r["ManagementPriority"] = "HIGH"
    elif abc_class == "B":
        r["ManagementPriority"] = "MEDIUM"
    else:
        r["ManagementPriority"] = "LOW"

output = os.path.join(
    BASE,
    "abc_intelligence.csv"
)

fields = [
    "DrugID",
    "GenericName",
    "UnitCost",
    "ObservedQuantity",
    "ObservationDays",
    "AnnualizedQuantity",
    "ObservedConsumptionValue",
    "AnnualizedConsumptionValue",
    "ConsumptionValuePercent",
    "CumulativeValuePercent",
    "ABCClass",
    "ManagementPriority",
    "DataSource",
    "DataStatus",
    "OperationalUse"
]

with open(
    output,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(results)

counts = {
    "A": 0,
    "B": 0,
    "C": 0
}

for r in results:
    counts[r["ABCClass"]] += 1

print()
print("Medicines analysed :", len(results))
print("Observation period :", observation_days, "days")
print()
print("Annual consumption value")
print("Total              :", round(total_value, 2))
print()
print("ABC classification:")
print("  A                :", counts["A"])
print("  B                :", counts["B"])
print("  C                :", counts["C"])
print()
print("Output:")
print("  abc_intelligence.csv")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
