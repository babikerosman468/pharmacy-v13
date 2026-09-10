inventory_sim.py (Option 24)

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


---

reorder_point.py (Option 25)

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


---

safety_stock.py (Option 26)

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


---

expiry_risk.py (Option 27)

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


---

abc_analysis.py (Option 28)

import json

with open("data/medicines.json") as f:
    meds = json.load(f)

items = []

for m in meds:

    value = m["quantity"] * m["price"]

    items.append(
        (m["name"], value)
    )

items.sort(
    key=lambda x: x[1],
    reverse=True
)

total = sum(v for _, v in items)

running = 0

print("\nABC ANALYSIS")
print("============")

for name, value in items:

    running += value

    pct = running / total * 100

    if pct <= 80:
        cls = "A"
    elif pct <= 95:
        cls = "B"
    else:
        cls = "C"

    print(name, cls)


---

eoq.py (Option 29)

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


---

ai_dashboard.py (Option 30)

import json

with open("data/medicines.json") as f:
    meds = json.load(f)

with open("data/sales.json") as f:
    sales = json.load(f)

inventory_value = sum(
    x["quantity"] * x["price"]
    for x in meds
)

revenue = sum(
    x["total"]
    for x in sales
)

low_stock = len(
    [x for x in meds if x["quantity"] <= 10]
)

print("\nAI DASHBOARD")
print("============")

print("Medicines:", len(meds))
print("Sales:", len(sales))
print("Revenue:", round(revenue, 2))
print("Inventory Value:", round(inventory_value, 2))
print("Low Stock Items:", low_stock)

print("\nRecommendations")

if low_stock > 0:
    print("- Replenish low stock medicines")

if revenue > 0:
    print("- Continue demand monitoring")

if inventory_value > 100000:
    print("- Review inventory turnover")

print("- Run Forecasting Module")
print("- Run ABC Analysis")
print("- Run EOQ Model")


        
