#!/usr/bin/env python3

"""
REEM V2 — PURE PYTHON DEMAND MODEL
===================================

Purpose:
    Baseline demand forecasting and validation.

Data source:
    schema/sales.csv
    schema/calendar.csv
    schema/medicines.csv

Output:
    demand_model.csv
    forecast_metrics.csv

Evidence boundary:
    SIMULATED_REEM_V2
    DEVELOPMENT
    NOT OPERATIONAL EVIDENCE

No third-party Python libraries.
"""

import csv
import math
import os
from datetime import datetime


BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(BASE, "schema")

SALES_FILE = os.path.join(SCHEMA, "sales.csv")
MEDICINES_FILE = os.path.join(SCHEMA, "medicines.csv")

MODEL_FILE = os.path.join(BASE, "demand_model.csv")
METRICS_FILE = os.path.join(BASE, "forecast_metrics.csv")


# ============================================================
# BASIC UTILITIES
# ============================================================

def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def date_value(value):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            pass
    return datetime.min


def mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def rmse(actual, predicted):
    if not actual:
        return 0.0

    total = 0.0

    for a, p in zip(actual, predicted):
        total += (a - p) ** 2

    return math.sqrt(total / len(actual))


def mae(actual, predicted):
    if not actual:
        return 0.0

    total = 0.0

    for a, p in zip(actual, predicted):
        total += abs(a - p)

    return total / len(actual)


def bias(actual, predicted):
    if not actual:
        return 0.0

    return mean(
        [p - a for a, p in zip(actual, predicted)]
    )


# ============================================================
# SALES PREPARATION
# ============================================================

def load_sales():
    rows = read_csv(SALES_FILE)

    data = {}

    for row in rows:

        drug = (
            row.get("DrugID")
            or row.get("drug_id")
            or row.get("MedicineID")
            or row.get("medicine_id")
        )

        timestamp = row.get("Timestamp", "")

        date = timestamp[:10]
        qty = (
            row.get("Quantity")
            or row.get("Qty")
            or row.get("SoldQty")
            or row.get("quantity")
        )

        if not drug or not date:
            continue

        quantity = number(qty)

        if drug not in data:
            data[drug] = {}

        if date not in data[drug]:
            data[drug][date] = 0.0

        data[drug][date] += quantity

    return data


# ============================================================
# MEDICINE MASTER
# ============================================================

def load_medicines():
    rows = read_csv(MEDICINES_FILE)

    medicines = {}

    for row in rows:

        drug = (
            row.get("DrugID")
            or row.get("drug_id")
            or row.get("MedicineID")
            or row.get("medicine_id")
        )

        if drug:
            medicines[drug] = row

    return medicines


# ============================================================
# COMPLETE DAILY SERIES
# ============================================================

def make_series(daily):

    if not daily:
        return []

    dates = sorted(
        daily.keys(),
        key=date_value
    )

    start = date_value(dates[0])
    end = date_value(dates[-1])

    values = []

    current = start

    while current <= end:

        key = current.strftime("%Y-%m-%d")

        values.append(
            (
                key,
                daily.get(key, 0.0)
            )
        )

        from datetime import timedelta

        current += timedelta(days=1)

    return values


# ============================================================
# FORECAST METHODS
# ============================================================

def naive_forecast(history):
    if not history:
        return 0.0

    return history[-1]


def moving_average(history, window=7):

    if not history:
        return 0.0

    values = history[-window:]

    return mean(values)


def weighted_moving_average(history, window=7):

    if not history:
        return 0.0

    values = history[-window:]

    if not values:
        return 0.0

    denominator = 0.0
    numerator = 0.0

    for i, value in enumerate(values, start=1):

        numerator += value * i
        denominator += i

    if denominator == 0:
        return 0.0

    return numerator / denominator


def trend_forecast(history, window=14):

    if not history:
        return 0.0

    values = history[-window:]

    if len(values) < 2:
        return mean(values)

    n = len(values)

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0

    for i, y in enumerate(values):

        x = i + 1

        sum_x += x
        sum_y += y
        sum_xy += x * y
        sum_x2 += x * x

    denominator = (
        n * sum_x2
        - sum_x * sum_x
    )

    if denominator == 0:
        return mean(values)

    slope = (
        n * sum_xy
        - sum_x * sum_y
    ) / denominator

    intercept = (
        sum_y
        - slope * sum_x
    ) / n

    forecast = intercept + slope * (n + 1)

    if forecast < 0:
        forecast = 0.0

    return forecast


# ============================================================
# BACK-TESTING
# ============================================================

def backtest(values, method, window=7, minimum=30):

    if len(values) <= minimum + 1:
        return [], []

    split = int(len(values) * 0.80)

    if split < minimum:
        return [], []

    train = values[:split]
    test = values[split:]

    actual = []
    predicted = []

    history = list(train)

    for value in test:

        if method == "NAIVE":
            prediction = naive_forecast(history)

        elif method == "MOVING_AVERAGE":
            prediction = moving_average(
                history,
                window
            )

        elif method == "WEIGHTED_MOVING_AVERAGE":
            prediction = weighted_moving_average(
                history,
                window
            )

        elif method == "TREND":
            prediction = trend_forecast(
                history,
                max(window, 14)
            )

        else:
            prediction = 0.0

        actual.append(value)
        predicted.append(prediction)

        # Expand history sequentially so that each
        # next forecast uses information available
        # up to that point.
        history.append(value)

    return actual, predicted

    if len(values) <= minimum:
        return [], []

    actual = []
    predicted = []

    for i in range(minimum, len(values)):

        history = values[:i]

        if method == "NAIVE":
            prediction = naive_forecast(history)

        elif method == "MOVING_AVERAGE":
            prediction = moving_average(
                history,
                window
            )

        elif method == "WEIGHTED_MOVING_AVERAGE":
            prediction = weighted_moving_average(
                history,
                window
            )

        elif method == "TREND":
            prediction = trend_forecast(
                history,
                max(window, 14)
            )

        else:
            prediction = 0.0

        actual.append(values[i])
        predicted.append(prediction)

    return actual, predicted


# ============================================================
# MAIN MODEL
# ============================================================

def run():

    print()
    print("=" * 60)
    print("REEM V2 — PURE PYTHON DEMAND MODEL")
    print("=" * 60)

    print()
    print("Loading medicines...")
    medicines = load_medicines()

    print("Loading sales...")
    sales = load_sales()

    print()
    print("Medicines with sales:", len(sales))

    model_rows = []
    metric_rows = []

    methods = [
        "NAIVE",
        "MOVING_AVERAGE",
        "WEIGHTED_MOVING_AVERAGE",
        "TREND"
    ]

    for drug in sorted(sales.keys()):

        series = make_series(
            sales[drug]
        )

        dates = [x[0] for x in series]
        values = [x[1] for x in series]

        if len(values) < 30:
            continue

        split = int(len(values) * 0.80)

        train = values[:split]
        test = values[split:]

        method_results = []

        for method in methods:

            actual, predicted = backtest(
                values,
                method,
                window=7,
                minimum=30
            )

            if not actual:
                continue

            error_mae = mae(
                actual,
                predicted
            )

            error_rmse = rmse(
                actual,
                predicted
            )

            error_bias = bias(
                actual,
                predicted
            )

            method_results.append(
                {
                    "method": method,
                    "mae": error_mae,
                    "rmse": error_rmse,
                    "bias": error_bias
                }
            )

            metric_rows.append(
                {
                    "DrugID": drug,
                    "Method": method,
                    "Observations": len(actual),
                    "MAE": round(error_mae, 4),
                    "RMSE": round(error_rmse, 4),
                    "Bias": round(error_bias, 4),
                    "DataSource": "SIMULATED_REEM_V2",
                    "DataStatus": "DEVELOPMENT"
                }
            )

        if not method_results:
            continue

        best = min(
            method_results,
            key=lambda x: x["mae"]
        )

        history_mean = mean(train)

        last_7 = moving_average(
            train,
            7
        )

        last_30 = moving_average(
            train,
            30
        )

        final_forecast = {
            "NAIVE": naive_forecast(train),
            "MOVING_AVERAGE": moving_average(
                train,
                7
            ),
            "WEIGHTED_MOVING_AVERAGE":
                weighted_moving_average(
                    train,
                    7
                ),
            "TREND": trend_forecast(
                train,
                14
            )
        }

        selected_forecast = final_forecast[
            best["method"]
        ]

        medicine = medicines.get(
            drug,
            {}
        )

        generic = (
            medicine.get("GenericName")
            or medicine.get("generic_name")
            or medicine.get("Generic")
            or ""
        )

        model_rows.append(
            {
                "DrugID": drug,
                "GenericName": generic,
                "ObservationDays": len(values),
                "TrainingDays": len(train),
                "ValidationDays": len(test),
                "MeanDailyDemand": round(
                    history_mean,
                    4
                ),
                "MA7": round(
                    last_7,
                    4
                ),
                "MA30": round(
                    last_30,
                    4
                ),
                "NaiveForecast": round(
                    final_forecast["NAIVE"],
                    4
                ),
                "MovingAverageForecast": round(
                    final_forecast[
                        "MOVING_AVERAGE"
                    ],
                    4
                ),
                "WeightedForecast": round(
                    final_forecast[
                        "WEIGHTED_MOVING_AVERAGE"
                    ],
                    4
                ),
                "TrendForecast": round(
                    final_forecast["TREND"],
                    4
                ),
                "SelectedModel": best["method"],
                "SelectedForecast": round(
                    selected_forecast,
                    4
                ),
                "SelectedMAE": round(
                    best["mae"],
                    4
                ),
                "SelectedRMSE": round(
                    best["rmse"],
                    4
                ),
                "SelectedBias": round(
                    best["bias"],
                    4
                ),
                "DataSource":
                    "SIMULATED_REEM_V2",
                "DataStatus":
                    "DEVELOPMENT",
                "OperationalUse":
                    "PROHIBITED"
            }
        )

    # ========================================================
    # WRITE MODEL OUTPUT
    # ========================================================

    if model_rows:

        fields = list(
            model_rows[0].keys()
        )

        with open(
            MODEL_FILE,
            "w",
            encoding="utf-8",
            newline=""
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(model_rows)

    # ========================================================
    # WRITE METRICS
    # ========================================================

    if metric_rows:

        fields = list(
            metric_rows[0].keys()
        )

        with open(
            METRICS_FILE,
            "w",
            encoding="utf-8",
            newline=""
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(metric_rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("DEMAND MODEL COMPLETE")
    print("=" * 60)

    print(
        "Models evaluated    :",
        len(metric_rows)
    )

    print(
        "Medicine forecasts  :",
        len(model_rows)
    )

    print()
    print("Output:")
    print("  demand_model.csv")
    print("  forecast_metrics.csv")

    print()
    print("Evidence boundary:")
    print("  DataSource      : SIMULATED_REEM_V2")
    print("  DataStatus      : DEVELOPMENT")
    print("  Operational use : PROHIBITED")

    print()
    print("=" * 60)


if __name__ == "__main__":
    run()

