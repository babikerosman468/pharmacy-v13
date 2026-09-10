import csv
import os
from collections import defaultdict

METRICS = "forecast_metrics.csv"
DEMAND = "demand_model.csv"
OUT = "report_data"

os.makedirs(OUT, exist_ok=True)

metrics = []
with open(METRICS, newline="", encoding="utf-8") as f:
    metrics = list(csv.DictReader(f))

demand = []
with open(DEMAND, newline="", encoding="utf-8") as f:
    demand = list(csv.DictReader(f))

methods = defaultdict(list)

for row in metrics:
    methods[row["Method"]].append(float(row["MAE"]))

method_mae = []

for method, values in methods.items():
    method_mae.append(
        (method, sum(values) / len(values))
    )

method_mae.sort(key=lambda x: x[1])

with open(
    os.path.join(OUT, "method_mae.tex"),
    "w",
    encoding="utf-8"
) as f:
    f.write(
        "Method & Mean MAE \\\\\n"
        "\\midrule\n"
    )

    for method, value in method_mae:
        f.write(
            method.replace("_", "\\_")
            + " & "
            + f"{value:.4f}"
            + " \\\\\n"
        )

selection = defaultdict(int)

for row in demand:
    selection[row["SelectedModel"]] += 1

with open(
    os.path.join(OUT, "model_selection.tex"),
    "w",
    encoding="utf-8"
) as f:
    f.write(
        "Model & Medicines \\\\\n"
        "\\midrule\n"
    )

    for method, count in sorted(
        selection.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        f.write(
            method.replace("_", "\\_")
            + " & "
            + str(count)
            + " \\\\\n"
        )

top = sorted(
    demand,
    key=lambda x: float(x["SelectedForecast"]),
    reverse=True
)[:10]

with open(
    os.path.join(OUT, "top_forecast.tex"),
    "w",
    encoding="utf-8"
) as f:
    f.write(
        "DrugID & Generic Name & Forecast \\\\\n"
        "\\midrule\n"
    )

    for row in top:
        name = row["GenericName"].replace("_", "\\_")
        f.write(
            f"{row['DrugID']} & {name} & "
            f"{float(row['SelectedForecast']):.2f} \\\\\n"
        )

print("=" * 60)
print("REEM V2 — REPORT DATA")
print("=" * 60)
print("Metrics rows :", len(metrics))
print("Demand rows  :", len(demand))
print("Models       :", len(selection))
print()
print("Generated:")
print("  report_data/method_mae.tex")
print("  report_data/model_selection.tex")
print("  report_data/top_forecast.tex")
print("=" * 60)
