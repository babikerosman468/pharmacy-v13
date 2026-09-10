import csv

rows = list(csv.DictReader(open("abc_intelligence.csv")))

print("=" * 60)
print("REEM V2 — ABC VALIDATION")
print("=" * 60)

for cls in ["A", "B", "C"]:
    subset = [r for r in rows if r["ABCClass"] == cls]

    value = sum(
        float(r["AnnualizedConsumptionValue"])
        for r in subset
    )

    print(
        cls,
        "Medicines:", len(subset),
        "Value:", round(value, 2)
    )

print()
print("Total medicines:", len(rows))

print(
    "Cumulative final:",
    rows[-1]["CumulativeValuePercent"],
    "%"
)

print(
    "Classes:",
    {x: sum(r["ABCClass"] == x for r in rows)
     for x in ["A", "B", "C"]}
)

print("=" * 60)
