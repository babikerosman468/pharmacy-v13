import csv

rows = list(csv.DictReader(open("inventory_intelligence.csv")))

def f(x):
    return float(x)

ratios = []
for r in rows:
    stock = f(r["CurrentStock"])
    rop = f(r["ReorderPoint"])
    ratio = stock / rop if rop > 0 else 0
    ratios.append((ratio, r["DrugID"], r["GenericName"], stock, rop))

print()
print("=" * 80)
print("REEM V2 — INVENTORY VALIDATION")
print("=" * 80)

print("Medicines:", len(rows))

print()
print("CURRENT STOCK")
print("Minimum :", min(f(r["CurrentStock"]) for r in rows))
print("Maximum :", max(f(r["CurrentStock"]) for r in rows))

print()
print("REORDER POINT")
print("Minimum :", min(f(r["ReorderPoint"]) for r in rows))
print("Maximum :", max(f(r["ReorderPoint"]) for r in rows))

print()
print("STOCK / REORDER POINT — LOWEST 10")
print("-" * 80)

for ratio, drug, name, stock, rop in sorted(ratios)[:10]:
    print(
        f"{drug:6} "
        f"{name:20.20} "
        f"Stock={stock:10.1f} "
        f"ROP={rop:8.2f} "
        f"Ratio={ratio:8.1f}"
    )

print()
print("STOCK / REORDER POINT — HIGHEST 10")
print("-" * 80)

for ratio, drug, name, stock, rop in sorted(ratios, reverse=True)[:10]:
    print(
        f"{drug:6} "
        f"{name:20.20} "
        f"Stock={stock:10.1f} "
        f"ROP={rop:8.2f} "
        f"Ratio={ratio:8.1f}"
    )

print()
print("=" * 80)
