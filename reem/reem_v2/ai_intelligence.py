import csv
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "reem_management_intelligence.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "ai_intelligence_context.json")


def read_data():
    with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(value):
    try:
        return float(value)
    except:
        return 0.0


def to_int(value):
    try:
        return int(float(value))
    except:
        return 0


def classify_signal(row):
    signals = []

    stock = to_float(row["CurrentStock"])
    coverage = to_float(row["CoverageDays"])
    rop = to_float(row["ReorderPoint"])
    safety = to_float(row["SafetyStock"])
    eoq = to_float(row["EOQ"])

    expired = to_int(row["ExpiredBatches"])
    critical = to_int(row["CriticalExpiryBatches"])
    high = to_int(row["HighExpiryBatches"])

    abc = row["ABCClass"]
    priority = row["ManagementPriority"]
    coverage_status = row["CoverageStatus"]
    rop_decision = row["ROPDecision"]

    if expired > 0:
        signals.append("EXPIRED_STOCK")

    if critical > 0:
        signals.append("CRITICAL_EXPIRY")

    if high > 0:
        signals.append("HIGH_EXPIRY")

    if rop_decision in ("STOCKOUT", "REORDER", "WATCH"):
        signals.append("REPLENISHMENT_SIGNAL")

    if coverage_status in ("STOCKOUT", "CRITICAL", "LOW"):
        signals.append("LOW_COVERAGE")

    if stock > 0 and rop > 0 and stock > rop * 10:
        signals.append("EXCESS_STOCK_SIGNAL")

    if abc == "A":
        signals.append("ABC_HIGH_VALUE")

    if priority == "HIGH":
        signals.append("HIGH_MANAGEMENT_PRIORITY")

    if not signals:
        signals.append("NO_MAJOR_SIGNAL")

    return signals


def management_interpretation(row, signals):
    statements = []

    stock = to_float(row["CurrentStock"])
    forecast = to_float(row["ForecastDailyDemand"])
    coverage = to_float(row["CoverageDays"])
    rop = to_float(row["ReorderPoint"])

    expired = to_int(row["ExpiredBatches"])
    critical = to_int(row["CriticalExpiryBatches"])

    if "EXPIRED_STOCK" in signals:
        statements.append(
            f"{expired} expired batch(es) are present in the analytical inventory data."
        )

    if "CRITICAL_EXPIRY" in signals:
        statements.append(
            f"{critical} batch(es) are classified as critical expiry risk."
        )

    if "REPLENISHMENT_SIGNAL" in signals:
        statements.append(
            f"The current replenishment assessment is {row['ROPDecision']}."
        )

    if "LOW_COVERAGE" in signals:
        statements.append(
            f"Forecast coverage is {coverage:.2f} days, indicating potential supply pressure."
        )

    if "EXCESS_STOCK_SIGNAL" in signals:
        statements.append(
            f"Current stock ({stock:.2f}) is substantially above the calculated reorder point ({rop:.2f})."
        )

    if forecast <= 0:
        statements.append(
            "The selected forecast is zero; demand interpretation should therefore be treated cautiously."
        )

    if not statements:
        statements.append(
            "No major management signal was detected from the integrated analytical evidence."
        )

    return statements


def build_record(row):
    signals = classify_signal(row)
    interpretation = management_interpretation(row, signals)

    return {
        "DrugID": row["DrugID"],
        "ForecastDailyDemand": to_float(row["ForecastDailyDemand"]),
        "ForecastModel": row["ForecastModel"],
        "ForecastMAE": to_float(row["ForecastMAE"]),
        "ABCClass": row["ABCClass"],
        "ManagementPriority": row["ManagementPriority"],
        "CurrentStock": to_float(row["CurrentStock"]),
        "CoverageDays": to_float(row["CoverageDays"]),
        "CoverageStatus": row["CoverageStatus"],
        "ReorderPoint": to_float(row["ReorderPoint"]),
        "ROPDecision": row["ROPDecision"],
        "SafetyStock": to_float(row["SafetyStock"]),
        "EOQ": to_float(row["EOQ"]),
        "ExpiredBatches": to_int(row["ExpiredBatches"]),
        "CriticalExpiryBatches": to_int(row["CriticalExpiryBatches"]),
        "HighExpiryBatches": to_int(row["HighExpiryBatches"]),
        "MediumExpiryBatches": to_int(row["MediumExpiryBatches"]),
        "LowExpiryBatches": to_int(row["LowExpiryBatches"]),
        "SupplierCount": to_int(row["SupplierCount"]),
        "HighReliabilitySuppliers": to_int(row["HighReliabilitySuppliers"]),
        "MediumReliabilitySuppliers": to_int(row["MediumReliabilitySuppliers"]),
        "LowReliabilitySuppliers": to_int(row["LowReliabilitySuppliers"]),
        "Signals": signals,
        "ManagementInterpretation": interpretation
    }


def build_ai_context(records):
    signal_counts = {}

    for record in records:
        for signal in record["Signals"]:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1

    context = {
        "system": "REEM V2 AI Intelligence",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "reem_management_intelligence.csv",
        "data_source": "SIMULATED_REEM_V2",
        "data_status": "DEVELOPMENT",
        "operational_use": "PROHIBITED",

        "architecture": {
            "role_of_reem": "Calculate analytical evidence",
            "role_of_ai": "Interpret, explain, prioritize and communicate analytical evidence",
            "ai_must_not": [
                "replace REEM model outputs",
                "silently recalculate validated metrics",
                "invent missing operational data",
                "present synthetic development data as real pharmacy evidence"
            ]
        },

        "summary": {
            "medicine_count": len(records),
            "signal_counts": signal_counts
        },

        "medicines": records
    }

    return context


def main():
    print("=" * 60)
    print("REEM V2 — AI INTELLIGENCE LAYER")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print()
        print("ERROR: reem_management_intelligence.csv not found.")
        print("Run reem_engine.py first.")
        return

    rows = read_data()
    records = [build_record(row) for row in rows]
    context = build_ai_context(records)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    print()
    print("Source records       :", len(rows))
    print("AI records            :", len(records))
    print("Output                :", os.path.basename(OUTPUT_FILE))
    print()
    print("Evidence boundary:")
    print("  DataSource          : SIMULATED_REEM_V2")
    print("  DataStatus          : DEVELOPMENT")
    print("  Operational use     : PROHIBITED")
    print()
    print("AI role:")
    print("  Interpret evidence")
    print("  Explain signals")
    print("  Prioritize issues")
    print("  Support management")
    print()
    print("AI layer status       : READY")
    print("=" * 60)


if __name__ == "__main__":
    main()
