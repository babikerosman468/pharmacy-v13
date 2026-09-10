import csv
import json
import random
from pathlib import Path
from datetime import datetime, date
BASE = Path("../..")
DATA = BASE / "data"
OUT = Path(".")
OUT.mkdir(exist_ok=True)


def load(name):
    with open(DATA / name, "r", encoding="utf-8") as f:
        return json.load(f)


def write_csv(name, rows, fields):
    path = OUT / name

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Created:", path)


def validate(medicines, sales, purchases):
    errors = []

    medicine_fields = [
        "id", "name", "quantity", "price", "expiry"
    ]

    sales_fields = [
        "medicine", "qty", "total", "date"
    ]

    purchase_fields = [
        "id", "supplierId", "supplierName",
        "medicineId", "medicineName",
        "quantity", "unitCost", "totalCost", "date"
    ]

    for i, x in enumerate(medicines):
        for field in medicine_fields:
            if field not in x:
                errors.append(f"Medicine {i}: missing {field}")

    for i, x in enumerate(sales):
        for field in sales_fields:
            if field not in x:
                errors.append(f"Sale {i}: missing {field}")

    for i, x in enumerate(purchases):
        for field in purchase_fields:
            if field not in x:
                errors.append(f"Purchase {i}: missing {field}")

    return errors


def parse_date(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).date()


def main():

    print("=" * 60)
    print("REEM V2 — ONE SHOT BUILD")
    print("=" * 60)

    medicines = load("medicines.json")
    sales = load("sales.json")
    purchases = load("purchases.json")
    suppliers = load("suppliers.json")

    print("Medicines :", len(medicines))
    print("Sales     :", len(sales))
    print("Purchases :", len(purchases))
    print("Suppliers :", len(suppliers))

    # ---------------------------------------------------------
    # 1. VALIDATION
    # ---------------------------------------------------------

    errors = validate(
        medicines,
        sales,
        purchases
    )

    print()
    print("VALIDATION")

    if errors:
        print("Errors :", len(errors))

        for error in errors:
            print("-", error)

        raise SystemExit("REEM V2 stopped because validation failed.")

    print("Errors : 0")
    print("Data validation : PASS")

    # ---------------------------------------------------------
    # 2. MEDICINE LOOKUP
    # ---------------------------------------------------------

    medicine_lookup = {
        m["name"].lower(): m
        for m in medicines
    }

    # ---------------------------------------------------------
    # 3. OBSERVED SALES
    # ---------------------------------------------------------

    dates = [
        parse_date(s["date"])
        for s in sales
    ]

    start_date = min(dates)
    end_date = max(dates)

    observation_days = (
        end_date - start_date
    ).days + 1

    observed = {}

    unmatched = []

    for sale in sales:

        key = sale["medicine"].lower()

        if key not in medicine_lookup:
            unmatched.append({
                "medicine": sale["medicine"],
                "qty": sale["qty"],
                "total": sale["total"],
                "date": sale["date"],
                "status": "UNMATCHED"
            })
            continue

        medicine = medicine_lookup[key]
        name = medicine["name"]

        if name not in observed:
            observed[name] = {
                "units": 0,
                "revenue": 0
            }

        observed[name]["units"] += sale["qty"]
        observed[name]["revenue"] += sale["total"]

    matched_units = sum(
        x["units"] for x in observed.values()
    )

    print()
    print("OBSERVED EVIDENCE")
    print("Start :", start_date)
    print("End   :", end_date)
    print("Days  :", observation_days)
    print("Matched units :", matched_units)
    print("Unmatched sales :", len(unmatched))

    # ---------------------------------------------------------
    # 4. DEMAND + COVERAGE + ABC
    # ---------------------------------------------------------

    demand_rows = []

    total_revenue = sum(
        x["revenue"] for x in observed.values()
    )

    for medicine in medicines:

        name = medicine["name"]

        units = observed.get(
            name,
            {"units": 0, "revenue": 0}
        )["units"]

        revenue = observed.get(
            name,
            {"units": 0, "revenue": 0}
        )["revenue"]

        daily_demand = (
            units / observation_days
            if observation_days > 0
            else 0
        )

        if daily_demand > 0:
            coverage_days = (
                medicine["quantity"]
                / daily_demand
            )
        else:
            coverage_days = None

        demand_rows.append({
            "Medicine": name,
            "Stock": medicine["quantity"],
            "ObservedUnits": units,
            "ObservedRevenue": revenue,
            "DailyDemand": round(daily_demand, 6),
            "CoverageDays": (
                round(coverage_days, 2)
                if coverage_days is not None
                else ""
            ),
            "DataSource": "OBSERVED_V13",
            "DataStatus": "OBSERVED"
        })

    # ABC based on observed revenue
    ranked = sorted(
        demand_rows,
        key=lambda x: float(x["ObservedRevenue"]),
        reverse=True
    )

    cumulative = 0

    for row in ranked:

        revenue = float(row["ObservedRevenue"])

        if total_revenue > 0:
            cumulative += revenue / total_revenue

            if cumulative <= 0.80:
                abc = "A"
            elif cumulative <= 0.95:
                abc = "B"
            else:
                abc = "C"
        else:
            abc = "C"

        row["ABC"] = abc
        row["ABCMethod"] = "OBSERVED-SALES"

    # restore medicine order
    demand_rows.sort(
        key=lambda x: x["Medicine"].lower()
    )

    write_csv(
        "demand.csv",
        demand_rows,
        [
            "Medicine",
            "Stock",
            "ObservedUnits",
            "ObservedRevenue",
            "DailyDemand",
            "CoverageDays",
            "ABC",
            "ABCMethod",
            "DataSource",
            "DataStatus"
        ]
    )

    # ---------------------------------------------------------
    # 5. DRUG INTELLIGENCE
    # ---------------------------------------------------------

    drug_rows = []

    for row in demand_rows:

        medicine = medicine_lookup[
            row["Medicine"].lower()
        ]

        expiry = date.fromisoformat(
            medicine["expiry"]
        )

        days_to_expiry = (
            expiry - end_date
        ).days

        if days_to_expiry < 0:
            expiry_risk = "EXPIRED"
        elif days_to_expiry <= 30:
            expiry_risk = "CRITICAL"
        elif days_to_expiry <= 90:
            expiry_risk = "HIGH"
        elif days_to_expiry <= 180:
            expiry_risk = "MEDIUM"
        else:
            expiry_risk = "LOW"

        if row["CoverageDays"] != "":
            coverage = float(row["CoverageDays"])

            if coverage > 365:
                stock_risk = "VERY_HIGH_COVERAGE"
            elif coverage > 180:
                stock_risk = "HIGH_COVERAGE"
            elif coverage > 90:
                stock_risk = "MODERATE_COVERAGE"
            else:
                stock_risk = "NORMAL"
        else:
            stock_risk = "NO_OBSERVED_DEMAND"

        drug_rows.append({
            "Medicine": row["Medicine"],
            "Stock": row["Stock"],
            "ObservedUnits": row["ObservedUnits"],
            "DailyDemand": row["DailyDemand"],
            "CoverageDays": row["CoverageDays"],
            "Expiry": medicine["expiry"],
            "DaysToExpiry": days_to_expiry,
            "ExpiryRisk": expiry_risk,
            "StockRisk": stock_risk,
            "ABC": row["ABC"],
            "DataSource": "OBSERVED_V13"
        })

    write_csv(
        "drugs.csv",
        drug_rows,
        [
            "Medicine",
            "Stock",
            "ObservedUnits",
            "DailyDemand",
            "CoverageDays",
            "Expiry",
            "DaysToExpiry",
            "ExpiryRisk",
            "StockRisk",
            "ABC",
            "DataSource"
        ]
    )

    # ---------------------------------------------------------
    # 6. SUPPLIER INTELLIGENCE
    # ---------------------------------------------------------

    supplier_rows = []

    for supplier in suppliers:

        purchases_supplier = [
            p for p in purchases
            if p["supplierId"] == supplier["id"]
        ]

        units = sum(
            p["quantity"]
            for p in purchases_supplier
        )

        cost = sum(
            p["totalCost"]
            for p in purchases_supplier
        )

        supplier_rows.append({
            "SupplierID": supplier["id"],
            "Supplier": supplier["name"],
            "PurchaseRecords": len(purchases_supplier),
            "PurchasedUnits": units,
            "ProcurementCost": cost,
            "DataSource": "OBSERVED_V13"
        })

    write_csv(
        "suppliers.csv",
        supplier_rows,
        [
            "SupplierID",
            "Supplier",
            "PurchaseRecords",
            "PurchasedUnits",
            "ProcurementCost",
            "DataSource"
        ]
    )

    # ---------------------------------------------------------
    # 7. RISK
    # ---------------------------------------------------------

    risk_rows = []

    for row in drug_rows:

        risk = "LOW"

        if row["ExpiryRisk"] in [
            "EXPIRED",
            "CRITICAL"
        ]:
            risk = "CRITICAL"
        elif row["ExpiryRisk"] == "HIGH":
            risk = "HIGH"
        elif row["StockRisk"] == "VERY_HIGH_COVERAGE":
            risk = "HIGH"
        elif row["StockRisk"] == "HIGH_COVERAGE":
            risk = "MODERATE"

        risk_rows.append({
            "Medicine": row["Medicine"],
            "ExpiryRisk": row["ExpiryRisk"],
            "StockRisk": row["StockRisk"],
            "OverallRisk": risk,
            "DataSource": "OBSERVED_V13"
        })

    write_csv(
        "risk.csv",
        risk_rows,
        [
            "Medicine",
            "ExpiryRisk",
            "StockRisk",
            "OverallRisk",
            "DataSource"
        ]
    )

    # ---------------------------------------------------------
    # 8. MODEL STATUS
    # ---------------------------------------------------------

    models = [
        ["Demand Forecasting", "PARTIAL",
         "Limited historical sales"],
        ["Observed-Sales ABC", "AVAILABLE",
         "Based on observed revenue"],
        ["Expiry Risk", "AVAILABLE",
         "Expiry dates available"],
        ["Stock Coverage", "AVAILABLE",
         "Observed demand available"],
        ["Supplier Analysis", "AVAILABLE",
         "Purchase history available"],
        ["Reorder Point", "PARTIAL",
         "Lead-time history unavailable"],
        ["Safety Stock", "PARTIAL",
         "Demand variability history limited"],
        ["EOQ", "PARTIAL",
         "Ordering and holding costs unavailable"],
        ["Monte Carlo", "READY_FOR_EXTENSION",
         "Longitudinal demand required"]
    ]

    model_rows = []

    for name, status, reason in models:
        model_rows.append({
            "Model": name,
            "Status": status,
            "Reason": reason
        })

    write_csv(
        "models.csv",
        model_rows,
        [
            "Model",
            "Status",
            "Reason"
        ]
    )

    # ---------------------------------------------------------
    # 9. MODEL ASSESSMENT
    # ---------------------------------------------------------

    metrics = [
        {
            "Model": "Demand Forecasting",
            "Metric": "MAE",
            "Value": "",
            "Status": "NOT_READY"
        },
        {
            "Model": "Demand Forecasting",
            "Metric": "RMSE",
            "Value": "",
            "Status": "NOT_READY"
        },
        {
            "Model": "Risk Classification",
            "Metric": "AUROC",
            "Value": "",
            "Status": "NOT_READY"
        },
        {
            "Model": "Risk Classification",
            "Metric": "Precision",
            "Value": "",
            "Status": "NOT_READY"
        },
        {
            "Model": "Risk Classification",
            "Metric": "Recall",
            "Value": "",
            "Status": "NOT_READY"
        },
        {
            "Model": "Risk Classification",
            "Metric": "F1",
            "Value": "",
            "Status": "NOT_READY"
        }
    ]

    write_csv(
        "metrics.csv",
        metrics,
        [
            "Model",
            "Metric",
            "Value",
            "Status"
        ]
    )

    # ---------------------------------------------------------
    # 10. DEVELOPMENT SYNTHETIC DATA
    # ---------------------------------------------------------

    random.seed(13)

    dev_rows = []

    medicines_with_demand = [
        name for name in observed
    ]

    if not medicines_with_demand:
        medicines_with_demand = [
            medicines[0]["name"]
        ]

    start = date(2024, 1, 1)

    for day in range(1096):

        current = start.fromordinal(
            start.toordinal() + day
        )

        day_of_week = current.weekday()
        day_of_year = current.timetuple().tm_yday

        for name in medicines_with_demand:

            if name in observed:
                observed_rate = (
                    observed[name]["units"]
                    / observation_days
                )
            else:
                observed_rate = 0.1

            base = max(
                observed_rate,
                0.05
            )

            weekly = 1.0

            if day_of_week >= 5:
                weekly = 0.85

            seasonal = (
                1.0
                + 0.20
                * __import__("math").sin(
                    2 * __import__("math").pi
                    * day_of_year
                    / 365.25
                )
            )

            noise = random.uniform(
                0.80,
                1.20
            )

            expected = (
                base
                * weekly
                * seasonal
                * noise
            )

            probability = min(
                expected,
                0.95
            )

            qty = 1 if random.random() < probability else 0

            dev_rows.append({
                "Date": current.isoformat(),
                "Medicine": name,
                "Qty": qty,
                "DataSource": "DEVELOPMENT_SYNTHETIC",
                "DataStatus": "DEVELOPMENT",
                "GeneratedFor": "MODEL_LEARNING",
                "NotOperationalEvidence": "TRUE"
            })

    write_csv(
        "dev_sales.csv",
        dev_rows,
        [
            "Date",
            "Medicine",
            "Qty",
            "DataSource",
            "DataStatus",
            "GeneratedFor",
            "NotOperationalEvidence"
        ]
    )

    # ---------------------------------------------------------
    # 11. SUMMARY
    # ---------------------------------------------------------

    summary = [
        ["MedicineCount", len(medicines)],
        ["SupplierCount", len(suppliers)],
        [
            "CurrentStockUnits",
            sum(m["quantity"] for m in medicines)
        ],
        [
            "CurrentStockValue",
            round(
                sum(
                    m["quantity"] * m["price"]
                    for m in medicines
                ),
                2
            )
        ],
        [
            "PurchasedUnits",
            sum(
                p["quantity"]
                for p in purchases
            )
        ],
        [
            "ProcurementCost",
            round(
                sum(
                    p["totalCost"]
                    for p in purchases
                ),
                2
            )
        ],
        ["MatchedSoldUnits", matched_units],
        ["UnmatchedSales", len(unmatched)],
        ["ObservationStart", start_date],
        ["ObservationEnd", end_date],
        ["ObservationDays", observation_days],
        [
            "CriticalExpiryItems",
            sum(
                1 for r in drug_rows
                if r["ExpiryRisk"] == "CRITICAL"
            )
        ]
    ]

    write_csv(
        "summary.csv",
        [
            {"Metric": x[0], "Value": x[1]}
            for x in summary
        ],
        ["Metric", "Value"]
    )

    # ---------------------------------------------------------
    # 12. UNMATCHED SALES
    # ---------------------------------------------------------

    write_csv(
        "unmatched.csv",
        unmatched,
        [
            "medicine",
            "qty",
            "total",
            "date",
            "status"
        ]
    )

    print()
    print("=" * 60)
    print("REEM V2 BUILD COMPLETE")
    print("=" * 60)

    print("Observed evidence :", "READY")
    print("Development data  :", "CREATED")
    print("Model assessment  :", "CREATED")
    print("Unmatched sales   :", len(unmatched))

    print()
    print("Output directory:")
    print(OUT.resolve())

    print("=" * 60)


if __name__ == "__main__":
    main()
