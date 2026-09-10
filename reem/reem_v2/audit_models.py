import csv
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "Demand Forecasting": ("demand_model.csv", 50),
    "ABC Analysis": ("abc_intelligence.csv", 50),
    "Expiry Risk": ("expiry_intelligence.csv", 792),
    "Stock Coverage": ("stock_coverage.csv", 50),
    "Supplier Analysis": ("supplier_intelligence.csv", 10),
    "Reorder Point": ("rop_intelligence.csv", 50),
    "Safety Stock": ("safety_stock_intelligence.csv", 50),
    "EOQ": ("eoq_intelligence.csv", 50)
}

print("=" * 60)
print("REEM V2 — 8-MODEL INTEGRITY AUDIT")
print("=" * 60)
print()

total_pass = 0
total_fail = 0

for model, (filename, expected_rows) in FILES.items():

    path = os.path.join(BASE, filename)

    if not os.path.exists(path):
        print("FAIL", model, "— file missing:", filename)
        total_fail += 1
        continue

    try:

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fields = reader.fieldnames or []

        checks = []

        checks.append(len(rows) == expected_rows)

        required_boundary = {
            "DataSource",
            "DataStatus"
        }

        if "OperationalUse" in fields:
            required_boundary.add("OperationalUse")

        checks.append(required_boundary.issubset(set(fields)))

        boundary_ok = True

        for row in rows:

            if row.get("DataSource") != "SIMULATED_REEM_V2":
                boundary_ok = False

            if row.get("DataStatus") != "DEVELOPMENT":
                boundary_ok = False

            if "OperationalUse" in fields:
                if row.get("OperationalUse") != "PROHIBITED":
                    boundary_ok = False

        checks.append(boundary_ok)

        numeric_ok = True

        for row in rows:

            for key, value in row.items():

                if value is None:
                    numeric_ok = False
                    continue

                value = value.strip()

                if value == "":
                    continue

                try:
                    number = float(value)

                    if not math.isfinite(number):
                        numeric_ok = False

                except ValueError:
                    pass

        checks.append(numeric_ok)

        if all(checks):

            print(
                "PASS",
                model,
                "| Rows:", len(rows),
                "| File:", filename
            )

            total_pass += 1

        else:

            print(
                "FAIL",
                model,
                "| Rows:", len(rows),
                "| Expected:", expected_rows,
                "| File:", filename
            )

            total_fail += 1

    except Exception as e:

        print("FAIL", model, "—", str(e))
        total_fail += 1

print()
print("-" * 60)
print("AUDIT SUMMARY")
print("-" * 60)
print()
print("Models passed :", total_pass)
print("Models failed :", total_fail)
print()

if total_fail == 0:

    print("STATUS : PASS")
    print()
    print("ALL 8 REEM V2 MODELS PASSED INTEGRITY AUDIT")
    print()
    print("Evidence boundary:")
    print("  DataSource      : SIMULATED_REEM_V2")
    print("  DataStatus      : DEVELOPMENT")
    print("  Operational use : PROHIBITED")

else:

    print("STATUS : FAIL")
    print()
    print("REVIEW FAILED MODELS BEFORE UI/DEPLOYMENT")

print("=" * 60)
