#=========================================
# Operations & Supply Management Analysis
# Pure Python Version (No Imports)
#=========================================

filename = "supply_chain.csv"

with open(filename, "r") as f:
    lines = f.readlines()

header = lines[0].strip().split(",")

data = []
for line in lines[1:]:
    values = line.strip().split(",")
    record = dict(zip(header, values))
    data.append(record)

print("Total Orders:", len(data))

total_units = 0
total_revenue = 0.0
supplier_summary = {}
product_summary = {}

for row in data:

    qty = int(row["Quantity"])
    revenue = float(row["Revenue"])
    supplier = row["Supplier"]
    product = row["Product"]

    total_units += qty
    total_revenue += revenue

    if supplier not in supplier_summary:
        supplier_summary[supplier] = {
            "Quantity": 0,
            "Revenue": 0.0
        }

    supplier_summary[supplier]["Quantity"] += qty
    supplier_summary[supplier]["Revenue"] += revenue

    if product not in product_summary:
        product_summary[product] = {
            "Quantity": 0,
            "Revenue": 0.0
        }

    product_summary[product]["Quantity"] += qty
    product_summary[product]["Revenue"] += revenue

print("Total Units:", total_units)
print("Total Revenue:", round(total_revenue, 2))

print("\nSupplier Performance")
for supplier in supplier_summary:
    print(
        supplier,
        supplier_summary[supplier]["Quantity"],
        supplier_summary[supplier]["Revenue"]
    )

print("\nProduct Summary")
for product in product_summary:
    print(
        product,
        product_summary[product]["Quantity"],
        product_summary[product]["Revenue"]
    )

with open("supplier_performance.csv", "w") as f:
    f.write("Supplier,Quantity,Revenue\n")
    for supplier in supplier_summary:
        f.write(
            "{},{},{}\n".format(
                supplier,
                supplier_summary[supplier]["Quantity"],
                supplier_summary[supplier]["Revenue"]
            )
        )

with open("product_summary.csv", "w") as f:
    f.write("Product,Quantity,Revenue\n")
    for product in product_summary:
        f.write(
            "{},{},{}\n".format(
                product,
                product_summary[product]["Quantity"],
                product_summary[product]["Revenue"]
            )
        )

print("\nAnalysis Complete.")

