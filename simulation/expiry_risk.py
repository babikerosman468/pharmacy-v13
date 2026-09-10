import json
from datetime import datetime

with open("data/medicines.json") as f:
    meds = json.load(f)

today = datetime.today()

print("\nEXPIRY RISK SIMULATION")
print("======================")

for m in meds:

    try:

        exp = datetime.strptime(
            m["expiry"],
            "%Y-%m-%d"
        )

        days = (exp - today).days

        if days < 90:

            print(
                m["name"],
                "HIGH RISK",
                days,
                "days"
            )

    except:
        pass


