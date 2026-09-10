import json
from pathlib import Path
from datetime import datetime


BASE = Path("..")
DATA = BASE / "data"


def load(name):
    path = DATA / name

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def observed_demand(medicines, sales):
    names = {}

    for medicine in medicines:
        names[medicine["name"].lower()] = medicine["name"]

    result = {}

    for sale in sales:
        name = sale["medicine"].lower()

        if name not in names:
            continue

        real_name = names[name]

        if real_name not in result:
            result[real_name] = 0

        result[real_name] += sale["qty"]

    return result


def validate_medicines(medicines):
    errors = []

    required = [
        "id",
        "name",
        "quantity",
        "price",
        "expiry"
    ]

    for i, medicine in enumerate(medicines):
        for field in required:
            if field not in medicine:
                errors.append(
                    f"Medicine {i}: missing {field}"
                )

    return errors


def validate_sales(sales):
    errors = []

    required = [
        "medicine",
        "qty",
        "total",
        "date"
    ]

    for i, sale in enumerate(sales):
        for field in required:
            if field not in sale:
                errors.append(
                    f"Sale {i}: missing {field}"
                )

    return errors


def validate_purchases(purchases):
    errors = []

    required = [
        "id",
        "supplierId",
        "supplierName",
        "medicineId",
        "medicineName",
        "quantity",
        "unitCost",
        "totalCost",
        "date"
    ]

    for i, purchase in enumerate(purchases):
        for field in required:
            if field not in purchase:
                errors.append(
                    f"Purchase {i}: missing {field}"
                )

    return errors

def main():

    medicines = load("medicines.json")
    sales = load("sales.json")
    purchases = load("purchases.json")
    suppliers = load("suppliers.json")

    medicine_errors = validate_medicines(medicines)
    sales_errors = validate_sales(sales)
    purchase_errors = validate_purchases(purchases)

    print("=" * 50)
    print("REEM V2")
    print("=" * 50)

    print("Medicines :", len(medicines))
    print("Sales     :", len(sales))
    print("Purchases :", len(purchases))
    print("Suppliers :", len(suppliers))

    print()
    print("VALIDATION")

    errors = (
        medicine_errors
        + sales_errors
        + purchase_errors
    )

    if errors:
        print("Errors :", len(errors))

        for error in errors:
            print("-", error)
    else:
        print("Errors : 0")
        print("Data validation : PASS")

    demand = observed_demand(
        medicines,
        sales
    )
    dates = []

    for sale in sales:
        dates.append(
            datetime.fromisoformat(
                sale["date"].replace("Z", "+00:00")
            )
        )

    if dates:
        start_date = min(dates).date()
        end_date = max(dates).date()
        observation_days = (
            end_date - start_date
        ).days + 1
    else:
        start_date = None
        end_date = None
        observation_days = 0

    total_demand = sum(demand.values())

    print()
    print("DEMAND OBSERVATION")
    print("Start :", start_date)
    print("End   :", end_date)
    print("Days  :", observation_days)
    print("Units :", total_demand)
    print()
    print("OBSERVED DEMAND")
    for medicine in medicines:
        name = medicine["name"]

        if name not in demand:
            continue

        daily = demand[name] / observation_days

        if daily > 0:
            coverage = medicine["quantity"] / daily
        else:
            coverage = None

        print(
            name,
            "| Stock:",
            medicine["quantity"],
            "| Days:",
            round(coverage, 1)
        )


if __name__ == "__main__":
    main()

