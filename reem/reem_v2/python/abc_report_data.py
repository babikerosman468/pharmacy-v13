import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, "abc_intelligence.csv")
OUT = os.path.join(BASE, "report_data")

os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))

def tex(s):
    return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")

total = sum(float(r["AnnualizedConsumptionValue"]) for r in rows)

classes = {}
for cls in ["A", "B", "C"]:
    subset = [r for r in rows if r["ABCClass"] == cls]
    value = sum(float(r["AnnualizedConsumptionValue"]) for r in subset)
    classes[cls] = {
        "count": len(subset),
        "value": value,
        "share": value / total * 100 if total else 0
    }

with open(os.path.join(OUT, "abc_summary.tex"), "w", encoding="utf-8") as f:
    f.write("\\newcommand{\\ABCTotalMedicines}{" + str(len(rows)) + "}\n")
    f.write("\\newcommand{\\ABCTotalValue}{" + f"{total:,.2f}" + "}\n")
    f.write("\\newcommand{\\ABCObservationDays}{" + str(rows[0]["ObservationDays"]) + "}\n")
    for cls in ["A", "B", "C"]:
        f.write(
            "\\newcommand{\\ABC" + cls + "Count}{" +
            str(classes[cls]["count"]) + "}\n"
        )
        f.write(
            "\\newcommand{\\ABC" + cls + "Value}{" +
            f"{classes[cls]['value']:,.2f}" + "}\n"
        )
        f.write(
            "\\newcommand{\\ABC" + cls + "Share}{" +
            f"{classes[cls]['share']:.2f}" + "\\%}\n"
        )

top = rows[:10]

with open(os.path.join(OUT, "abc_top10.tex"), "w", encoding="utf-8") as f:
    for i, r in enumerate(top, 1):
        f.write(
            f"{i} & {tex(r['DrugID'])} & {tex(r['GenericName'])} & "
            f"{float(r['AnnualizedConsumptionValue']):,.2f} & "
            f"{float(r['ConsumptionValuePercent']):.2f}\\% & "
            f"{float(r['CumulativeValuePercent']):.2f}\\% & "
            f"{r['ABCClass']} \\\\\n"
        )

with open(os.path.join(OUT, "abc_curve.tex"), "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, 1):
        f.write(
            f"({i},{float(r['CumulativeValuePercent']):.4f}) "
        )

with open(os.path.join(OUT, "abc_class.tex"), "w", encoding="utf-8") as f:
    for cls in ["A", "B", "C"]:
        f.write(
            f"{cls} & {classes[cls]['count']} & "
            f"{classes[cls]['share']:.2f}\\% & "
            f"{classes[cls]['value']:,.2f} \\\\\n"
        )

print("=" * 60)
print("REEM V2 — ABC REPORT DATA")
print("=" * 60)
print()
print("Medicines :", len(rows))
print("Observation days :", rows[0]["ObservationDays"])
print("Total annualized value :", f"{total:,.2f}")
print()
print("ABC classes:")
for cls in ["A", "B", "C"]:
    print(
        f"  {cls} : {classes[cls]['count']:2d} medicines  "
        f"{classes[cls]['share']:.2f}%  "
        f"{classes[cls]['value']:,.2f}"
    )
print()
print("Generated:")
print("  report_data/abc_summary.tex")
print("  report_data/abc_top10.tex")
print("  report_data/abc_curve.tex")
print("  report_data/abc_class.tex")
print("=" * 60)
