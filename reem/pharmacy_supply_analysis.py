# ============================================================
# PHARMACY V13
# Supply Chain & Drug Management Analysis
# ============================================================
#
# Purpose:
#   Transform supply-chain transactions into management
#   information for Pharmacy V13.
#
# Core identity:
#   Every drug is identified by DrugID.
#
# Outputs:
#   - supplier_performance.csv
#   - drug_summary.csv
#   - management_summary.csv
#
# Architecture:
#   Operational Data
#        ↓
#   Structured Information
#        ↓
#   Drug / Supplier / Financial Analysis
#        ↓
#   Pharmacy V13 Decision-Support Layer
#
# ============================================================


INPUT_FILE = "supply_chain.csv"

SUPPLIER_OUTPUT = "supplier_performance.csv"
DRUG_OUTPUT = "drug_summary.csv"
MANAGEMENT_OUTPUT = "management_summary.csv"


# ============================================================
# READ DATA
# ============================================================

with open(INPUT_FILE, "r") as f:
    lines = f.readlines()

header = lines[0].strip().split(",")

data = []

for line in lines[1:]:

    if not line.strip():
        continue

    values = line.strip().split(",")

    record = dict(zip(header, values))

    data.append(record)


print("=" * 60)
print("PHARMACY V13")
print("SUPPLY CHAIN & DRUG MANAGEMENT ANALYSIS")
print("=" * 60)


# ============================================================
# BASIC DATA CHECK
# ============================================================

print("\nRecords:", len(data))

print("\nFields detected:")

for field in header:
    print(" -", field)


# ============================================================
# SUMMARY VARIABLES
# ============================================================

total_orders = len(data)

total_units = 0
total_revenue = 0.0

supplier_summary = {}
drug_summary = {}


# ============================================================
# PROCESS TRANSACTIONS
# ============================================================

for row in data:

    # --------------------------------------------------------
    # Drug identity
    # --------------------------------------------------------

    if "DrugID" in row:
        drug_id = row["DrugID"]

    elif "Drug ID" in row:
        drug_id = row["Drug ID"]

    elif "ProductID" in row:
        drug_id = row["ProductID"]

    elif "Product ID" in row:
        drug_id = row["Product ID"]

    else:
        raise ValueError(
            "No Drug ID field found in supply_chain.csv"
        )


    # --------------------------------------------------------
    # Optional drug name
    # --------------------------------------------------------

    if "DrugName" in row:
        drug_name = row["DrugName"]

    elif "Drug Name" in row:
        drug_name = row["Drug Name"]

    elif "Product" in row:
        drug_name = row["Product"]

    else:
        drug_name = ""


    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    qty = int(row["Quantity"])


    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue = float(row["Revenue"])


    # --------------------------------------------------------
    # Supplier
    # --------------------------------------------------------

    supplier = row["Supplier"]


    # --------------------------------------------------------
    # Global totals
    # --------------------------------------------------------

    total_units += qty
    total_revenue += revenue


    # ========================================================
    # SUPPLIER ANALYSIS
    # ========================================================

    if supplier not in supplier_summary:

        supplier_summary[supplier] = {
            "Quantity": 0,
            "Revenue": 0.0,
            "Orders": 0
        }

    supplier_summary[supplier]["Quantity"] += qty
    supplier_summary[supplier]["Revenue"] += revenue
    supplier_summary[supplier]["Orders"] += 1


    # ========================================================
    # DRUG ANALYSIS
    # ========================================================

    if drug_id not in drug_summary:

        drug_summary[drug_id] = {
            "DrugName": drug_name,
            "Quantity": 0,
            "Revenue": 0.0,
            "Orders": 0
        }

    drug_summary[drug_id]["Quantity"] += qty
    drug_summary[drug_id]["Revenue"] += revenue
    drug_summary[drug_id]["Orders"] += 1


# ============================================================
# MANAGEMENT SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("MANAGEMENT SUMMARY")
print("=" * 60)

print("Total Orders:", total_orders)
print("Total Units:", total_units)
print("Total Revenue:", round(total_revenue, 2))

print("Number of Suppliers:", len(supplier_summary))
print("Number of Drugs:", len(drug_summary))


# ============================================================
# SUPPLIER PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("SUPPLIER PERFORMANCE")
print("=" * 60)

for supplier in supplier_summary:

    s = supplier_summary[supplier]

    print(
        supplier,
        "| Orders:", s["Orders"],
        "| Quantity:", s["Quantity"],
        "| Revenue:", round(s["Revenue"], 2)
    )


# ============================================================
# DRUG SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DRUG SUMMARY")
print("=" * 60)

for drug_id in drug_summary:

    d = drug_summary[drug_id]

    print(
        drug_id,
        "|",
        d["DrugName"],
        "| Orders:", d["Orders"],
        "| Quantity:", d["Quantity"],
        "| Revenue:", round(d["Revenue"], 2)
    )


# ============================================================
# WRITE SUPPLIER PERFORMANCE
# ============================================================

with open(SUPPLIER_OUTPUT, "w") as f:

    f.write(
        "Supplier,Orders,Quantity,Revenue\n"
    )

    for supplier in supplier_summary:

        s = supplier_summary[supplier]

        f.write(
            "{},{},{},{}\n".format(
                supplier,
                s["Orders"],
                s["Quantity"],
                round(s["Revenue"], 2)
            )
        )


# ============================================================
# WRITE DRUG SUMMARY
# ============================================================

with open(DRUG_OUTPUT, "w") as f:

    f.write(
        "DrugID,DrugName,Orders,Quantity,Revenue\n"
    )

    for drug_id in drug_summary:

        d = drug_summary[drug_id]

        f.write(
            "{},{},{},{},{}\n".format(
                drug_id,
                d["DrugName"],
                d["Orders"],
                d["Quantity"],
                round(d["Revenue"], 2)
            )
        )


# ============================================================
# WRITE MANAGEMENT SUMMARY
# ============================================================

with open(MANAGEMENT_OUTPUT, "w") as f:

    f.write(
        "Metric,Value\n"
    )

    f.write(
        "Total Orders,{}\n".format(total_orders)
    )

    f.write(
        "Total Units,{}\n".format(total_units)
    )

    f.write(
        "Total Revenue,{}\n".format(round(total_revenue, 2))
    )

    f.write(
        "Number of Suppliers,{}\n".format(len(supplier_summary))
    )

    f.write(
        "Number of Drugs,{}\n".format(len(drug_summary))
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)

print("\nGenerated:")
print(" -", SUPPLIER_OUTPUT)
print(" -", DRUG_OUTPUT)
print(" -", MANAGEMENT_OUTPUT)

print("\nPharmacy V13 analytical layer ready.")
