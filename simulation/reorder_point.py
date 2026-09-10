
import json

with open("data/medicines.json") as f:
    meds = json.load(f)

print("\nREORDER POINT MODEL")
print("===================")

for m in meds:

    daily_demand = max(1, int(m["quantity"] * 0.05))

    lead_time = 7

    reorder_point = daily_demand * lead_time

    print(
        m["name"],
        "ROP:",
        reorder_point
    )


