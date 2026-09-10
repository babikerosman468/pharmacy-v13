import json
import random

with open("data/medicines.json") as f:
    meds = json.load(f)

print("\nINVENTORY RISK ANALYSIS")
print("=======================")

for m in meds:

    failures = 0

    for _ in range(1000):

        demand = random.randint(0, 100)

        if demand > m["quantity"]:
            failures += 1

    risk = failures / 1000 * 100

    print(
        m["name"],
        "Risk:",
        round(risk, 1),
        "%"
    )

