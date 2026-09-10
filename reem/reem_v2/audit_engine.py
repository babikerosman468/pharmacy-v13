import csv
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE, "reem_management_intelligence.csv")

EXPECTED_ROWS = 50

REQUIRED_FIELDS = [
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

NUMERIC_FIELDS = [
    "ForecastDailyDemand",
    "ForecastMAE",
    "CurrentStock",
    "CoverageDays",
    "ReorderPoint",
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
    "LowReliabilitySuppliers"
]

print("=" * 60)
print("REEM V2 — ENGINE INTEGRATION AUDIT")
print("=" * 60)
print()

if not os.path.exists(FILE):

    print("STATUS : FAIL")
    print()
    print("Missing:", FILE)
    print("=" * 60)
    raise SystemExit(1)

with open(FILE, newline="", encoding="utf-8") as f:

    reader = csv.DictReader(f)
    fields = reader.fieldnames or []
    rows = list(reader)

checks = []

row_count_ok = len(rows) == EXPECTED_ROWS
checks.append(row_count_ok)

print(
    ("PASS" if row_count_ok else "FAIL"),
    "Row count:",
    len(rows),
    "| Expected:", EXPECTED_ROWS
)

field_check = all(field in fields for field in REQUIRED_FIELDS)
checks.append(field_check)

print(
    ("PASS" if field_check else "FAIL"),
    "Required fields:",
    len(REQUIRED_FIELDS)
)

drug_ids = [r.get("DrugID", "").strip() for r in rows]

unique_ids = len(set(drug_ids)) == EXPECTED_ROWS
no_missing_ids = all(drug_ids)

checks.append(unique_ids)
checks.append(no_missing_ids)

print(
    ("PASS" if unique_ids else "FAIL"),
    "Unique DrugIDs:", len(set(drug_ids))
)

print(
    ("PASS" if no_missing_ids else "FAIL"),
    "Missing DrugIDs:", drug_ids.count("")
)

numeric_ok = True

for row in rows:

    for field in NUMERIC_FIELDS:

        value = row.get(field, "").strip()

        if value == "":
            numeric_ok = False
            continue

        try:
            number = float(value)

            if not math.isfinite(number):
                numeric_ok = False

        except ValueError:
            numeric_ok = False

checks.append(numeric_ok)

print(
    ("PASS" if numeric_ok else "FAIL"),
    "Numeric integrity"
)

boundary_ok = True

for row in rows:

    if row.get("DataSource") != "SIMULATED_REEM_V2":
        boundary_ok = False

    if row.get("DataStatus") != "DEVELOPMENT":
        boundary_ok = False

    if row.get("OperationalUse") != "PROHIBITED":
        boundary_ok = False

checks.append(boundary_ok)

print(
    ("PASS" if boundary_ok else "FAIL"),
    "Evidence boundary"
)

model_values = set(r.get("ForecastModel", "") for r in rows)

model_ok = model_values.issubset({
    "NAIVE",
    "MOVING_AVERAGE",
    "WEIGHTED_MOVING_AVERAGE",
    "TREND"
})

checks.append(model_ok)

print(
    ("PASS" if model_ok else "FAIL"),
    "Forecast model integrity"
)

abc_values = set(r.get("ABCClass", "") for r in rows)

abc_ok = abc_values.issubset({"A", "B", "C"})
checks.append(abc_ok)

print(
    ("PASS" if abc_ok else "FAIL"),
    "ABC classification integrity"
)

coverage_values = set(r.get("CoverageStatus", "") for r in rows)

coverage_ok = coverage_values.issubset({
    "STOCKOUT",
    "CRITICAL",
    "LOW",
    "ADEQUATE",
    "HIGH"
})

checks.append(coverage_ok)

print(
    ("PASS" if coverage_ok else "FAIL"),
    "Coverage status integrity"
)

rop_values = set(r.get("ROPDecision", "") for r in rows)

rop_ok = rop_values.issubset({
    "STOCKOUT",
    "REORDER",
    "WATCH",
    "ADEQUATE"
})

checks.append(rop_ok)

print(
    ("PASS" if rop_ok else "FAIL"),
    "ROP decision integrity"
)

print()
print("-" * 60)
print("INTEGRATION SUMMARY")
print("-" * 60)
print()

passed = sum(checks)
failed = len(checks) - passed

print("Checks passed :", passed)
print("Checks failed :", failed)
print()

if failed == 0:

    print("STATUS : PASS")
    print()
    print("REEM INTELLIGENCE ENGINE INTEGRATION PASSED")
    print()
    print("8 MODELS → ENGINE → 50 MEDICINES")
    print()
    print("Evidence boundary:")
    print("  DataSource      : SIMULATED_REEM_V2")
    print("  DataStatus      : DEVELOPMENT")
    print("  Operational use : PROHIBITED")

else:

    print("STATUS : FAIL")
    print()
    print("REVIEW FAILED INTEGRATION CHECKS")

print("=" * 60)
