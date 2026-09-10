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



