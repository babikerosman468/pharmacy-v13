import csv
import math
import os
from statistics import mean, pstdev
from datetime import datetime

BASE = "schema"

DEMAND_FILE = "demand_model.csv"
SALES_FILE = os.path.join(BASE, "sales.csv")
PURCHASE_FILE = os.path.join(BASE, "purchases.csv")
DELIVERY_FILE = os.path.join(BASE, "deliveries.csv")
MOVEMENT_FILE = os.path.join(BASE, "stock_movements.csv")
MEDICINE_FILE = os.path.join(BASE, "medicines.csv")

OUTPUT = "inventory_intelligence.csv"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def number(value):
    try:
        return float(value)
    except:
        return 0.0


def parse_date(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "")).date()
    except:
        return None


def load():
    demand = read_csv(DEMAND_FILE)
    medicines = read_csv(MEDICINE_FILE)
    purchases = read_csv(PURCHASE_FILE)
    deliveries = read_csv(DELIVERY_FILE)
    movements = read_csv(MOVEMENT_FILE)

    return demand, medicines, purchases, deliveries, movements


def build():
    demand, medicines, purchases, deliveries, movements = load()

    medicine_info = {
        r["DrugID"]: r for r in medicines
    }

    lead_times = {}

    for row in deliveries:

        drug_id = row.get("DrugID", "")

        lead = number(row.get("LeadTimeDays"))

        if drug_id and lead >= 0:
            lead_times.setdefault(drug_id, []).append(lead)

    current_stock = {}


    for row in read_csv(
        os.path.join(BASE, "inventory_batches.csv")
    ):
        drug_id = row.get("DrugID", "")
        quantity = number(
            row.get("RemainingQuantity")
        )

        current_stock[drug_id] = (
            current_stock.get(drug_id, 0.0)
            + quantity
        )
    results = []

    for row in demand:

        drug_id = row["DrugID"]

        daily = number(row["MeanDailyDemand"])
        forecast = number(row["SelectedForecast"])
        validation_mae = number(row["SelectedMAE"])

        lead = lead_times.get(drug_id, [])

        if lead:
            avg_lead = mean(lead)
            lead_sd = pstdev(lead) if len(lead) > 1 else 0.0
            lead_status = "OBSERVED"
        else:
            avg_lead = 7.0
            lead_sd = 0.0
            lead_status = "ASSUMED_7_DAYS"

        demand_lead = forecast * avg_lead

        demand_sd = validation_mae

        safety_stock = (
            1.65
            * demand_sd
            * math.sqrt(avg_lead)
        )

        reorder_point = (
            demand_lead
            + safety_stock
        )

        stock = current_stock.get(
            drug_id,
            0.0
        )

        if stock <= 0:
            decision = "STOCKOUT_RISK"

        elif stock <= reorder_point:
            decision = "REORDER"

        elif stock <= reorder_point * 1.5:
            decision = "WATCH"
        else:
            decision = "ADEQUATE"

        medicine = medicine_info.get(
            drug_id,
            {}
        )

        results.append({
            "DrugID": drug_id,
            "GenericName": medicine.get(
                "GenericName",
                ""
            ),
            "SelectedModel": row["SelectedModel"],
            "ForecastUnitsPerDay": round(
                forecast,
                4
            ),
            "MeanDailyDemand": round(
                daily,
                4
            ),
            "ValidationMAE": round(
                validation_mae,
                4
            ),
            "LeadTimeDays": round(
                avg_lead,
                2
            ),
            "LeadTimeStatus": lead_status,
            "DemandDuringLeadTime": round(
                demand_lead,
                2
            ),
            "SafetyStock": round(
                safety_stock,
                2
            ),
            "ReorderPoint": round(
                reorder_point,
                2
            ),
            "CurrentStock": round(
            stock,
                2
            ),
            "InventoryDecision": decision,
            "DataSource": "SIMULATED_REEM_V2",
            "DataStatus": "DEVELOPMENT",
            "OperationalUse": "PROHIBITED"
        })

    results.sort(
        key=lambda x: (
            {
                "STOCKOUT_RISK": 0,
                "REORDER": 1,
                "WATCH": 2,
                "ADEQUATE": 3
            }.get(
                x["InventoryDecision"],
                9
            ),
            -x["ReorderPoint"]
        )
    )

    fields = list(results[0].keys())

    with open(
        OUTPUT,
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

    return results
def main():

    print("=" * 60)
    print("REEM V2 — INVENTORY INTELLIGENCE")
    print("=" * 60)

    results = build()

    counts = {}

    for row in results:
        decision = row["InventoryDecision"]
        counts[decision] = counts.get(decision, 0) + 1

    print()
    print("Medicines analysed :", len(results))
    print()
    print("Inventory decisions:")

    for key in [
        "STOCKOUT_RISK",
        "REORDER",
        "WATCH",
        "ADEQUATE"
    ]:
        print(
            f"  {key:16} : {counts.get(key, 0)}"
        )

    print()
    print("Output:")
    print("  inventory_intelligence.csv")

    print()
    print("Evidence boundary:")
    print("  DataSource      : SIMULATED_REEM_V2")
    print("  DataStatus      : DEVELOPMENT")
    print("  Operational use : PROHIBITED")

    print("=" * 60)


if __name__ == "__main__":
    main()
