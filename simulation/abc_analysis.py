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


