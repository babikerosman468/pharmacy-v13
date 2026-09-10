import json
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, "ai_intelligence_context.json")
OUTPUT = os.path.join(BASE, "ai_management_decisions.json")


def load():
    with open(INPUT, encoding="utf-8") as f:
        return json.load(f)


def priority(signals):
    if "CRITICAL_EXPIRY" in signals:
        return "HIGH"
    if "LOW_COVERAGE" in signals:
        return "HIGH"
    if "REPLENISHMENT_SIGNAL" in signals:
        return "HIGH"
    if "EXPIRED_STOCK" in signals:
        return "MEDIUM"
    if "EXCESS_STOCK_SIGNAL" in signals:
        return "MEDIUM"
    if "ABC_HIGH_VALUE" in signals:
        return "MEDIUM"
    return "LOW"


def primary_signal(signals):
    order = [
        "CRITICAL_EXPIRY",
        "LOW_COVERAGE",
        "REPLENISHMENT_SIGNAL",
        "EXPIRED_STOCK",
        "HIGH_EXPIRY",
        "EXCESS_STOCK_SIGNAL",
        "ABC_HIGH_VALUE"
    ]

    for item in order:
        if item in signals:
            return item

    return "NO_MAJOR_SIGNAL"


def actions(signals):
    result = []

    if "CRITICAL_EXPIRY" in signals:
        result.append("Review critical-expiry batches immediately.")

    if "EXPIRED_STOCK" in signals:
        result.append("Review expired inventory and verify physical stock.")

    if "LOW_COVERAGE" in signals:
        result.append("Review replenishment requirements.")

    if "REPLENISHMENT_SIGNAL" in signals:
        result.append("Review the reorder signal before procurement.")

    if "EXCESS_STOCK_SIGNAL" in signals:
        result.append("Review excess inventory before additional purchasing.")

    if "ABC_HIGH_VALUE" in signals:
        result.append("Give this medicine higher management attention.")

    if not result:
        result.append("No immediate management action indicated.")

    return result


def interpret(row, signals):
    result = []

    if row["ExpiredBatches"] > 0:
        result.append(
            f'{row["ExpiredBatches"]} expired batch(es) are present.'
        )

    if row["CriticalExpiryBatches"] > 0:
        result.append(
            f'{row["CriticalExpiryBatches"]} critical-expiry batch(es) are present.'
        )

    if row["CurrentStock"] > row["ReorderPoint"] * 10:
        result.append(
            f'Current stock ({row["CurrentStock"]:.2f}) is substantially above '
            f'the reorder point ({row["ReorderPoint"]:.2f}).'
        )

    if row["ForecastDailyDemand"] <= 0:
        result.append(
            "The selected forecast is zero; demand interpretation requires caution."
        )

    if not result:
        result.append(
            "No major management signal was detected."
        )

    return result


def convert(row):
    return {
        "DrugID": row["DrugID"],
        "ForecastDailyDemand": float(row["ForecastDailyDemand"]),
        "ForecastModel": row["ForecastModel"],
        "ForecastMAE": float(row["ForecastMAE"]),
        "ABCClass": row["ABCClass"],
        "ManagementPriority": row["ManagementPriority"],
        "CurrentStock": float(row["CurrentStock"]),
        "CoverageDays": float(row["CoverageDays"]),
        "CoverageStatus": row["CoverageStatus"],
        "ReorderPoint": float(row["ReorderPoint"]),
        "ROPDecision": row["ROPDecision"],
        "SafetyStock": float(row["SafetyStock"]),
        "EOQ": float(row["EOQ"]),
        "ExpiredBatches": int(row["ExpiredBatches"]),
        "CriticalExpiryBatches": int(row["CriticalExpiryBatches"]),
        "HighExpiryBatches": int(row["HighExpiryBatches"]),
        "Signals": row["Signals"]
    }


def decision(row):
    signals = row["Signals"]

    return {
        "DrugID": row["DrugID"],
        "Priority": priority(signals),
        "PrimarySignal": primary_signal(signals),
        "Evidence": convert(row),
        "Interpretation": interpret(row, signals),
        "RecommendedAction": actions(signals)
    }


def main():
    print("=" * 60)
    print("REEM V2 — AI DECISION INTELLIGENCE")
    print("=" * 60)

    if not os.path.exists(INPUT):
        print("ERROR: ai_intelligence_context.json not found.")
        return

    context = load()

    decisions = [
        decision(row)
        for row in context["medicines"]
    ]

    order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2
    }

    decisions.sort(
        key=lambda x: order.get(x["Priority"], 9)
    )

    counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for item in decisions:
        counts[item["Priority"]] += 1

    output = {
        "system": "REEM V2 AI Decision Intelligence",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": context["source"],
        "data_source": context["data_source"],
        "data_status": context["data_status"],
        "operational_use": context["operational_use"],
        "medicine_count": len(decisions),
        "priority_counts": counts,
        "decisions": decisions
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Medicines analysed :", len(decisions))
    print("HIGH               :", counts["HIGH"])
    print("MEDIUM             :", counts["MEDIUM"])
    print("LOW                :", counts["LOW"])
    print()
    print("Data source        :", context["data_source"])
    print("Data status        :", context["data_status"])
    print("Operational use    :", context["operational_use"])
    print()
    print("Output             :", os.path.basename(OUTPUT))
    print("AI Decision Layer  : READY")
    print("=" * 60)


if __name__ == "__main__":
    main()
