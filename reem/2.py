import json
p="../data/medicines.json"
x=json.load(open(p,encoding="utf-8"))
print("records:", len(x))
print(json.dumps(x[:3], indent=2, ensure_ascii=False))

import json
p="../data/sales.json"
x=json.load(open(p,encoding="utf-8"))
print("records:", len(x))
print(json.dumps(x[:5], indent=2, ensure_ascii=False))
import json
p="../data/purchases.json"
x=json.load(open(p,encoding="utf-8"))
print("records:", len(x))
print(json.dumps(x[:5], indent=2, ensure_ascii=False))
import json
p="../data/suppliers.json"
x=json.load(open(p,encoding="utf-8"))
print("records:", len(x))
print(json.dumps(x[:5], indent=2, ensure_ascii=False))
