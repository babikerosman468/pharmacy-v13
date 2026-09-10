#!/usr/bin/env python3

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, date

BASE = ".."
DATA = f"{BASE}/data"

MEDICINES_FILE = f"{DATA}/medicines.json"
PURCHASES_FILE = f"{DATA}/purchases.json"
SALES_FILE = f"{DATA}/sales.json"
SUPPLIERS_FILE = f"{DATA}/suppliers.json"

OUT_DIR = "."

DAYS_IN_YEAR = 365


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()
    except Exception:
        try:
            return datetime.strptime(
                value[:10],
                "%Y-%m-%d"
            ).date()
        except Exception:
            return None


def write_csv(filename, rows, fieldnames):
    path = f"{OUT_DIR}/{filename}"

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {path}")


def main():

    medicines = load_json(MEDICINES_FILE)
    purchases = load_json(PURCHASES_FILE)
    sales = load_json(SALES_FILE)
    suppliers = load_json(SUPPLIERS_FILE)

    print("=" * 70)
    print("PHARMACY V13 — SUPPLY INTELLIGENCE")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. AUTHORITATIVE MEDICINE MASTER
    # ------------------------------------------------------------

    medicine_by_id = {}
    medicine_by_name = {}

    for m in medicines:
        mid = str(m.get("id"))
        name = str(
            m.get("name", "")
        ).strip()

        medicine_by_id[mid] = m

        if name:
            medicine_by_name[
                name.lower()
            ] = m

    # ------------------------------------------------------------
    # 2. SUPPLIER MASTER
    # ------------------------------------------------------------

    supplier_by_id = {
        str(s.get("id")): s
        for s in suppliers
    }

    # ------------------------------------------------------------
    # 3. PURCHASE AGGREGATION
    # ------------------------------------------------------------

    purchase_qty = defaultdict(float)
    purchase_cost = defaultdict(float)
    supplier_qty = defaultdict(float)
    supplier_cost = defaultdict(float)

    for p in purchases:

        mid = str(
            p.get("medicineId")
        )

        qty = float(
            p.get("quantity", 0) or 0
        )

        cost = float(
            p.get("totalCost", 0) or 0
        )

        purchase_qty[mid] += qty
        purchase_cost[mid] += cost

        sid = str(
            p.get("supplierId")
        )

        supplier_qty[sid] += qty
        supplier_cost[sid] += cost

    # ------------------------------------------------------------
    # 3B. SALES OBSERVATION WINDOW
    # ------------------------------------------------------------

    sales_dates = []

    for s in sales:

        d = parse_date(
            s.get("date")
        )

        if d:
            sales_dates.append(d)

    if sales_dates:

        observation_start = min(
            sales_dates
        )

        observation_end = max(
            sales_dates
        )

        observation_days = (
            observation_end
            - observation_start
        ).days + 1

        observation_days = max(
            observation_days,
            1
        )

    else:

        observation_start = None
        observation_end = None
        observation_days = 1

    print(
        f"Sales observation period: "
        f"{observation_start} to "
        f"{observation_end} "
        f"({observation_days} days)"
    )

    # ------------------------------------------------------------
    # 4. SALES AGGREGATION
    # ------------------------------------------------------------

    sales_qty = defaultdict(float)
    sales_revenue = defaultdict(float)

    unmatched_sales = []

    for s in sales:

        name = str(
            s.get("medicine", "")
        ).strip()

        qty = float(
            s.get("qty", 0) or 0
        )

        revenue = float(
            s.get("total", 0) or 0
        )

        medicine = medicine_by_name.get(
            name.lower()
        )

        if medicine is None:

            unmatched_sales.append({
                "Medicine": name,
                "Quantity": qty,
                "Revenue": revenue,
                "Date": s.get(
                    "date",
                    ""
                )
            })

            continue

        mid = str(
            medicine["id"]
        )

        sales_qty[mid] += qty
        sales_revenue[mid] += revenue

    # ------------------------------------------------------------
    # 5. ANALYTICAL MEDICINE DATASET
    # ------------------------------------------------------------

    rows = []

    today = date.today()

    for mid, medicine in medicine_by_id.items():

        name = medicine.get(
            "name",
            ""
        )

        stock = float(
            medicine.get(
                "quantity",
                0
            ) or 0
        )

        price = float(
            medicine.get(
                "price",
                0
            ) or 0
        )

        purchased = purchase_qty[mid]
        procurement_cost = purchase_cost[mid]

        sold = sales_qty[mid]
        revenue = sales_revenue[mid]

        if purchased > 0:

            avg_unit_cost = (
                procurement_cost
                / purchased
            )

        else:

            avg_unit_cost = 0

        if sold > 0:

            estimated_margin = (
                revenue
                - (
                    sold
                    * avg_unit_cost
                )
            )

        else:

            estimated_margin = 0

        # Current stock value
        stock_value = (
            stock * price
        )

        # Demand based on the actual
        # sales observation window.
        daily_demand = (
            sold
            / observation_days
        )

        # Simple demand-based reorder indicator.
        # This is NOT a final ROP because
        # historical lead time is not currently
        # present in purchases.json.
        reorder_signal = (

            "REVIEW"

            if (
                sold > 0
                and stock <= max(
                    1,
                    daily_demand * 30
                )
            )

            else "OK"
        )

        # --------------------------------------------------------
        # Expiry analysis
        # --------------------------------------------------------

        expiry = medicine.get(
            "expiry",
            ""
        )

        expiry_date = parse_date(
            expiry
        )

        if expiry_date:

            days_to_expiry = (
                expiry_date
                - today
            ).days

        else:

            days_to_expiry = ""

        if isinstance(
            days_to_expiry,
            int
        ):

            if days_to_expiry < 0:

                expiry_status = "EXPIRED"

            elif days_to_expiry <= 90:

                expiry_status = "CRITICAL"

            elif days_to_expiry <= 180:

                expiry_status = "WATCH"

            else:

                expiry_status = "OK"

        else:

            expiry_status = "UNKNOWN"

        # Approximate days of stock coverage
        if daily_demand > 0:

            stock_days = (
                stock
                / daily_demand
            )

        else:

            stock_days = ""

        rows.append({

            "DrugID": mid,

            "DrugName": name,

            "CurrentStock": stock,

            "SellingPrice": price,

            "StockValue": round(
                stock_value,
                2
            ),

            "PurchasedQty": purchased,

            "ProcurementCost": round(
                procurement_cost,
                2
            ),

            "SoldQty": sold,

            "Revenue": round(
                revenue,
                2
            ),

            "AverageUnitCost": round(
                avg_unit_cost,
                2
            ),

            "EstimatedMargin": round(
                estimated_margin,
                2
            ),

            "DailyDemand": round(
                daily_demand,
                4
            ),

            "ObservationDays":
                observation_days,

            "StockDays": (
                round(
                    stock_days,
                    2
                )
                if stock_days != ""
                else ""
            ),

            "ReorderSignal":
                reorder_signal,

            "Expiry": expiry,

            "DaysToExpiry":
                days_to_expiry,

            "ExpiryStatus":
                expiry_status
        })

    # ------------------------------------------------------------
    # 6. OBSERVED-SALES ABC ANALYSIS
    # ------------------------------------------------------------

    rows.sort(
        key=lambda x:
            x["Revenue"],
        reverse=True
    )

    total_revenue = sum(
        r["Revenue"]
        for r in rows
    )

    cumulative = 0

    for r in rows:

        if total_revenue > 0:

            cumulative += (
                r["Revenue"]
            )

            pct = (
                cumulative
                / total_revenue
            )

            if pct <= 0.80:

                abc = "A"

            elif pct <= 0.95:

                abc = "B"

            else:

                abc = "C"

        else:

            abc = "C"

        r["ABC_Class"] = abc

        # Explicitly identify the
        # evidence basis of this ABC.
        r["ABC_Method"] = (
            "Observed-Sales ABC"
        )

    # ------------------------------------------------------------
    # 7. SUPPLIER INTELLIGENCE
    # ------------------------------------------------------------

    supplier_rows = []

    for sid, supplier in supplier_by_id.items():

        qty = supplier_qty[sid]
        cost = supplier_cost[sid]

        supplier_rows.append({

            "SupplierID": sid,

            "SupplierName":
                supplier.get(
                    "name",
                    ""
                ),

            "PurchasedQty": qty,

            "ProcurementCost":
                round(
                    cost,
                    2
                )
        })

    # ------------------------------------------------------------
    # 8. MANAGEMENT SUMMARY
    # ------------------------------------------------------------

    total_stock = sum(
        r["CurrentStock"]
        for r in rows
    )

    total_stock_value = sum(
        r["StockValue"]
        for r in rows
    )

    total_sales_qty = sum(
        r["SoldQty"]
        for r in rows
    )

    total_revenue = sum(
        r["Revenue"]
        for r in rows
    )

    total_procurement = sum(
        r["ProcurementCost"]
        for r in rows
    )

    expiry_critical = sum(
        1
        for r in rows
        if r["ExpiryStatus"]
        in (
            "EXPIRED",
            "CRITICAL"
        )
    )

    reorder_reviews = sum(
        1
        for r in rows
        if r["ReorderSignal"]
        == "REVIEW"
    )

    abc_a = sum(
        1
        for r in rows
        if r["ABC_Class"]
        == "A"
    )

    summary = [

        {
            "Metric":
                "MedicineCount",

            "Value":
                len(rows)
        },

        {
            "Metric":
                "SupplierCount",

            "Value":
                len(suppliers)
        },

        {
            "Metric":
                "CurrentStockUnits",

            "Value":
                total_stock
        },

        {
            "Metric":
                "CurrentStockValue",

            "Value":
                round(
                    total_stock_value,
                    2
                )
        },

        {
            "Metric":
                "PurchasedUnits",

            "Value":
                sum(
                    purchase_qty.values()
                )
        },

        {
            "Metric":
                "ProcurementCost",

            "Value":
                round(
                    total_procurement,
                    2
                )
        },

        {
            "Metric":
                "SoldUnits",

            "Value":
                total_sales_qty
        },

        {
            "Metric":
                "SalesRevenue",

            "Value":
                round(
                    total_revenue,
                    2
                )
        },

        {
            "Metric":
                "CriticalExpiryItems",

            "Value":
                expiry_critical
        },

        {
            "Metric":
                "ReorderReviewItems",

            "Value":
                reorder_reviews
        },

        {
            "Metric":
                "ABC_A_Items",

            "Value":
                abc_a
        },

        {
            "Metric":
                "UnmatchedSalesRecords",

            "Value":
                len(unmatched_sales)
        },

        {
            "Metric":
                "SalesObservationStart",

            "Value":
                (
                    observation_start.isoformat()
                    if observation_start
                    else ""
                )
        },

        {
            "Metric":
                "SalesObservationEnd",

            "Value":
                (
                    observation_end.isoformat()
                    if observation_end
                    else ""
                )
        },

        {
            "Metric":
                "SalesObservationDays",

            "Value":
                observation_days
        }
    ]

    # ------------------------------------------------------------
    # 9. MODEL READINESS
    # ------------------------------------------------------------

    model_rows = [

        {
            "Model":
                "Demand Forecasting",

            "Status":
                "AVAILABLE",

            "Basis":
                "Observed sales transactions over actual observation window"
        },

        {
            "Model":
                "ABC Analysis",

            "Status":
                "AVAILABLE",

            "Basis":
                "Observed-sales revenue; preliminary until mature history is available"
        },

        {
            "Model":
                "Expiry Risk",

            "Status":
                "AVAILABLE",

            "Basis":
                "Medicine expiry dates and current stock"
        },

        {
            "Model":
                "Stock Coverage",

            "Status":
                "AVAILABLE",

            "Basis":
                "Current stock versus observed demand"
        },

        {
            "Model":
                "Supplier Analysis",

            "Status":
                "AVAILABLE",

            "Basis":
                "Purchase quantities and procurement cost"
        },

        {
            "Model":
                "Reorder Point",

            "Status":
                "PARTIAL",

            "Basis":
                "Lead-time history not currently recorded"
        },

        {
            "Model":
                "Safety Stock",

            "Status":
                "PARTIAL",

            "Basis":
                "Demand variability and lead-time history required"
        },

        {
            "Model":
                "EOQ",

            "Status":
                "PARTIAL",

            "Basis":
                "Ordering and holding-cost parameters required"
        },

        {
            "Model":
                "Monte Carlo",

            "Status":
                "READY_FOR_EXTENSION",

            "Basis":
                "Demand distribution and lead-time uncertainty"
        }
    ]

    # ------------------------------------------------------------
    # 10. WRITE OUTPUTS
    # ------------------------------------------------------------

    write_csv(
        "v13_drug_intelligence.csv",
        rows,
        list(rows[0].keys())
        if rows
        else []
    )

    write_csv(
        "v13_supplier_intelligence.csv",
        supplier_rows,
        [
            "SupplierID",
            "SupplierName",
            "PurchasedQty",
            "ProcurementCost"
        ]
    )

    write_csv(
        "v13_management_summary.csv",
        summary,
        [
            "Metric",
            "Value"
        ]
    )

    write_csv(
        "v13_model_readiness.csv",
        model_rows,
        [
            "Model",
            "Status",
            "Basis"
        ]
    )

    if unmatched_sales:

        write_csv(
            "v13_unmatched_sales.csv",
            unmatched_sales,
            [
                "Medicine",
                "Quantity",
                "Revenue",
                "Date"
            ]
        )

    print()
    print("=" * 70)
    print("V13 SUPPLY INTELLIGENCE COMPLETE")
    print("=" * 70)

    print(
        f"Medicines analysed : {len(rows)}"
    )

    print(
        f"Suppliers analysed : {len(suppliers)}"
    )

    print(
        f"Sales records      : {len(sales)}"
    )

    print(
        f"Purchase records   : {len(purchases)}"
    )

    print(
        f"Unmatched sales    : {len(unmatched_sales)}"
    )

    print(
        f"Critical expiry    : {expiry_critical}"
    )

    print(
        f"Reorder reviews    : {reorder_reviews}"
    )

    print()

    print(
        "Important:"
    )

    print(
        "ROP/Safety Stock/EOQ are not fabricated."
    )

    print(
        "They will be activated when the required"
    )

    print(
        "historical parameters are available."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
