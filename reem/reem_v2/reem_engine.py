import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "demand": "demand_model.csv",
    "abc": "abc_intelligence.csv",
    "expiry": "expiry_intelligence.csv",
    "coverage": "stock_coverage.csv",
    "supplier": "supplier_intelligence.csv",
    "rop": "rop_intelligence.csv",
    "safety": "safety_stock_intelligence.csv",
    "eoq": "eoq_intelligence.csv"
}

def read_csv(filename):
    path = os.path.join(BASE, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def index_by_drug(rows):
    return {r["DrugID"]: r for r in rows if "DrugID" in r}

demand_rows = read_csv(FILES["demand"])
abc_rows = read_csv(FILES["abc"])
expiry_rows = read_csv(FILES["expiry"])
coverage_rows = read_csv(FILES["coverage"])
supplier_rows = read_csv(FILES["supplier"])
rop_rows = read_csv(FILES["rop"])
safety_rows = read_csv(FILES["safety"])
eoq_rows = read_csv(FILES["eoq"])

demand = index_by_drug(demand_rows)
abc = index_by_drug(abc_rows)
coverage = index_by_drug(coverage_rows)
rop = index_by_drug(rop_rows)
safety = index_by_drug(safety_rows)
eoq = index_by_drug(eoq_rows)

expiry_summary = {}

for r in expiry_rows:

    drug = r["DrugID"]
    risk = r.get("ExpiryRisk", "")

    if drug not in expiry_summary:
        expiry_summary[drug] = {
            "EXPIRED": 0,
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "NO_STOCK": 0
        }

    if risk in expiry_summary[drug]:
        expiry_summary[drug][risk] += 1

supplier_count = len(supplier_rows)

high_suppliers = sum(
    1 for r in supplier_rows
    if r.get("SupplierReliability") == "HIGH"
)

medium_suppliers = sum(
    1 for r in supplier_rows
    if r.get("SupplierReliability") == "MEDIUM"
)

low_suppliers = sum(
    1 for r in supplier_rows
    if r.get("SupplierReliability") == "LOW"
)

drug_ids = sorted(
    set(demand)
    & set(abc)
    & set(coverage)
    & set(rop)
    & set(safety)
    & set(eoq)
)

rows = []

for drug in drug_ids:

    ex = expiry_summary.get(
        drug,
        {
            "EXPIRED": 0,
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "NO_STOCK": 0
        }
    )

    rows.append({
        "DrugID": drug,
        "ForecastDailyDemand": demand[drug].get("SelectedForecast", "0"),
        "ForecastModel": demand[drug].get("SelectedModel", ""),
        "ForecastMAE": demand[drug].get("SelectedMAE", "0"),
        "ABCClass": abc[drug].get("ABCClass", ""),
        "ManagementPriority": abc[drug].get("ManagementPriority", ""),
        "CurrentStock": coverage[drug].get("CurrentStock", "0"),
        "CoverageDays": coverage[drug].get("CoverageDays", "0"),
        "CoverageStatus": coverage[drug].get("CoverageStatus", ""),
        "ReorderPoint": rop[drug].get("ReorderPoint", "0"),
        "ROPDecision": rop[drug].get("Decision", ""),
        "SafetyStock": safety[drug].get("SafetyStock", "0"),
        "EOQ": eoq[drug].get("EOQ", "0"),
        "ExpiredBatches": ex["EXPIRED"],
        "CriticalExpiryBatches": ex["CRITICAL"],
        "HighExpiryBatches": ex["HIGH"],
        "MediumExpiryBatches": ex["MEDIUM"],
        "LowExpiryBatches": ex["LOW"],
        "SupplierCount": supplier_count,
        "HighReliabilitySuppliers": high_suppliers,
        "MediumReliabilitySuppliers": medium_suppliers,
        "LowReliabilitySuppliers": low_suppliers,
        "DataSource": "SIMULATED_REEM_V2",
        "DataStatus": "DEVELOPMENT",
        "OperationalUse": "PROHIBITED"
    })

OUTPUT = os.path.join(BASE, "reem_management_intelligence.csv")

fields = [
    "DrugID",
    "ForecastDailyDemand",
    "ForecastModel",
    "ForecastMAE",
    "ABCClass",
    "ManagementPriority",
    "CurrentStock",
    "CoverageDays",
    "CoverageStatus",
    "ReorderPoint",
    "ROPDecision",
    "SafetyStock",
    "EOQ",
    "ExpiredBatches",
    "CriticalExpiryBatches",
    "HighExpiryBatches",
    "MediumExpiryBatches",
    "LowExpiryBatches",
    "SupplierCount",
    "HighReliabilitySuppliers",
    "MediumReliabilitySuppliers",
    "LowReliabilitySuppliers",
    "DataSource",
    "DataStatus",
    "OperationalUse"
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("=" * 60)
print("REEM V2 — INTELLIGENCE ENGINE")
print("=" * 60)
print()
print("Models integrated   : 8")
print("Medicines integrated:", len(rows))
print("Suppliers available :", supplier_count)
print()
print("Management output:")
print("  reem_management_intelligence.csv")
print()
print("Engine status       : READY")
print()
print("Evidence boundary:")
print("  DataSource      : SIMULATED_REEM_V2")
print("  DataStatus      : DEVELOPMENT")
print("  Operational use : PROHIBITED")
print("=" * 60)
