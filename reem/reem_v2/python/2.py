import csv

rows = list(csv.DictReader(open("inventory_intelligence.csv")))

checks = {
    "50 medicines": len(rows) == 50,
    "No negative stock": all(float(r["CurrentStock"]) >= 0 for r in rows),
    "ROP positive": all(float(r["ReorderPoint"]) >= 0 for r in rows),
    "Lead time observed": all(r["LeadTimeStatus"] == "OBSERVED" for r in rows),
    "No missing decisions": all(r["InventoryDecision"] for r in rows),
    "Development boundary": all(r["DataStatus"] == "DEVELOPMENT" for r in rows),
    "Operational prohibited": all(r["OperationalUse"] == "PROHIBITED" for r in rows)
}

print()
print("=" * 60)
print("REEM V2 — INVENTORY INTEGRITY CHECK")
print("=" * 60)

for name, result in checks.items():
    print(f"{'PASS' if result else 'FAIL':5}  {name}")

print("=" * 60)
