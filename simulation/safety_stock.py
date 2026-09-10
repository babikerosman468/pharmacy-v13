import json
import math

with open("data/medicines.json") as f:
    meds = json.load(f)

print("\nSAFETY STOCK MODEL")
print("==================")

for m in meds:

    daily_demand = max(1, int(m["quantity"] * 0.05))

    lead_time = 7

    z = 1.65

    safety_stock = round(
        z * math.sqrt(lead_time) * daily_demand
    )

    print(
        m["name"],
        "Safety Stock:",
        safety_stock
    )


