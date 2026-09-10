import json
import math

with open("data/medicines.json") as f:
    meds = json.load(f)

print("\nEOQ MODEL")
print("=========")

for m in meds:

    demand = max(
        100,
        m["quantity"] * 12
    )

    ordering_cost = 50

    holding_cost = max(
        1,
        m["price"] * 0.2
    )

    eoq = round(
        math.sqrt(
            (2 * demand * ordering_cost)
            / holding_cost
        )
    )

    print(
        m["name"],
        "EOQ:",
        eoq
    )

