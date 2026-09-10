#!/data/data/com.termux/files/usr/bin/bash

set -e

ROOT="$HOME/pharmacy-v13"
cd "$ROOT"

echo "============================================================"
echo " PHARMACY V13 — ONESHOT8"
echo " SUPPLIER + PURCHASE + STOCK-IN FOUNDATION"
echo "============================================================"

STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="backups/oneshot8_${STAMP}"

mkdir -p "$BACKUP"

echo
echo "[1/7] Creating backup..."

cp web_server.js "$BACKUP/web_server.js"
cp data/medicines.json "$BACKUP/medicines.json"
cp data/suppliers.json "$BACKUP/suppliers.json"
cp data/purchases.json "$BACKUP/purchases.json"
cp data/audit.json "$BACKUP/audit.json"

echo "Backup: $BACKUP"

echo
echo "[2/7] Validating JSON..."

python3 -c 'import json; json.load(open("data/medicines.json")); print("PASS: medicines.json")'
python3 -c 'import json; json.load(open("data/suppliers.json")); print("PASS: suppliers.json")'
python3 -c 'import json; json.load(open("data/purchases.json")); print("PASS: purchases.json")'
python3 -c 'import json; json.load(open("data/audit.json")); print("PASS: audit.json")'

echo
echo "[3/7] Creating inventory API backup copy..."

cp web_server.js "$BACKUP/web_server.js.pre_inventory"

echo "PASS: source protected"

echo
echo "[4/7] Preparing inventory API..."

python3 -c '
from pathlib import Path

p = Path("web_server.js")
s = p.read_text(encoding="utf-8")

if "function writeJSON(file, data)" in s:
    print("Inventory helpers already present.")
    raise SystemExit(0)

marker = "function json(res, data, status = 200) {"

helper = """function writeJSON(file, data) {
    const temp = file + ".tmp";
    fs.writeFileSync(
        temp,
        JSON.stringify(data, null, 2),
        "utf8"
    );
    fs.renameSync(temp, file);
}

function readRequestBody(req) {
    return new Promise((resolve, reject) => {
        let body = "";

        req.on("data", chunk => {
            body += chunk;

            if (body.length > 1024 * 1024) {
                reject(new Error("Request body too large"));
                req.destroy();
            }
        });

        req.on("end", () => {
            if (!body.trim()) {
                resolve({});
                return;
            }

            try {
                resolve(JSON.parse(body));
            } catch {
                reject(new Error("Invalid JSON"));
            }
        });

        req.on("error", reject);
    });
}

function audit(action, details = {}) {
    const file = path.join(DATA, "audit.json");
    const logs = readJSON(file);

    logs.push({
        action,
        time: new Date().toISOString(),
        ...details
    });

    writeJSON(file, logs);
}

function nextId(records) {
    if (!records.length) return 1;

    return Math.max(
        ...records.map(x => Number(x.id) || 0)
    ) + 1;
}

"""

if marker not in s:
    raise SystemExit("ERROR: json() function not found")

s = s.replace(marker, helper + marker, 1)

p.write_text(s, encoding="utf-8")

print("PASS: inventory helpers installed")
'

echo
echo "PART 1 COMPLETE."
echo "Do not run the script yet."
echo "Save nano with:"
echo "  CTRL+O"
echo "  ENTER"
echo "  CTRL+X"

echo
echo "[5/7] Installing Supplier + Purchase + Stock-In APIs..."

python3 -c '
from pathlib import Path

p = Path("web_server.js")
s = p.read_text(encoding="utf-8")

if "/api/inventory/stock-in" in s:
    print("Inventory API already installed.")
    raise SystemExit(0)

marker = "    // --------------------------------------------------------\n    // EXISTING / CORE API\n    // --------------------------------------------------------"

routes = r"""
    // --------------------------------------------------------
    // SUPPLIER API
    // --------------------------------------------------------

    if (req.method === "GET" && url.pathname === "/api/suppliers") {
        return json(
            res,
            readJSON(path.join(DATA, "suppliers.json"))
        );
    }

    if (req.method === "POST" && url.pathname === "/api/suppliers") {
        readRequestBody(req)
            .then(body => {

                const name = String(body.name || "").trim();
                const phone = String(body.phone || "").trim();
                const address = String(body.address || "").trim();

                if (!name) {
                    return json(
                        res,
                        { error: "Supplier name is required" },
                        400
                    );
                }

                const file = path.join(DATA, "suppliers.json");
                const suppliers = readJSON(file);

                const duplicate = suppliers.find(
                    s =>
                        String(s.name || "").toLowerCase() ===
                        name.toLowerCase()
                );

                if (duplicate) {
                    return json(
                        res,
                        {
                            error: "Supplier already exists",
                            supplier: duplicate
                        },
                        409
                    );
                }

                const supplier = {
                    id: nextId(suppliers),
                    name,
                    phone,
                    address,
                    createdAt: new Date().toISOString()
                };

                suppliers.push(supplier);
                writeJSON(file, suppliers);

                audit("SUPPLIER_ADD", {
                    supplierId: supplier.id,
                    supplierName: supplier.name
                });

                return json(res, supplier, 201);
            })
            .catch(error => {
                return json(
                    res,
                    { error: error.message },
                    400
                );
            });

        return;
    }

    // --------------------------------------------------------
    // PURCHASE API
    // --------------------------------------------------------

    if (req.method === "GET" && url.pathname === "/api/purchases") {
        return json(
            res,
            readJSON(path.join(DATA, "purchases.json"))
        );
    }

    if (req.method === "POST" && url.pathname === "/api/purchases") {
        readRequestBody(req)
            .then(body => {

                const supplierId = Number(body.supplierId);
                const medicineId = Number(body.medicineId);
                const quantity = Number(body.quantity);
                const unitCost = Number(body.unitCost || 0);

                if (!Number.isInteger(supplierId) || supplierId <= 0) {
                    return json(
                        res,
                        { error: "Valid supplierId is required" },
                        400
                    );
                }

                if (!Number.isInteger(medicineId) || medicineId <= 0) {
                    return json(
                        res,
                        { error: "Valid medicineId is required" },
                        400
                    );
                }

                if (!Number.isFinite(quantity) || quantity <= 0) {
                    return json(
                        res,
                        { error: "Quantity must be greater than zero" },
                        400
                    );
                }

                if (!Number.isFinite(unitCost) || unitCost < 0) {
                    return json(
                        res,
                        { error: "Unit cost cannot be negative" },
                        400
                    );
                }

                const suppliers = readJSON(
                    path.join(DATA, "suppliers.json")
                );

                const medicines = readJSON(
                    path.join(DATA, "medicines.json")
                );

                const supplier = suppliers.find(
                    s => Number(s.id) === supplierId
                );

                if (!supplier) {
                    return json(
                        res,
                        { error: "Supplier not found" },
                        404
                    );
                }

                const medicine = medicines.find(
                    m => Number(m.id) === medicineId
                );

                if (!medicine) {
                    return json(
                        res,
                        { error: "Medicine not found" },
                        404
                    );
                }

                const file = path.join(DATA, "purchases.json");
                const purchases = readJSON(file);

                const purchase = {
                    id: nextId(purchases),
                    supplierId,
                    supplierName: supplier.name,
                    medicineId,
                    medicineName: medicine.name,
                    quantity,
                    unitCost,
                    totalCost: quantity * unitCost,
                    date: body.date || new Date().toISOString(),
                    batchNumber: String(body.batchNumber || "").trim(),
                    expiry: String(body.expiry || "").trim(),
                    createdAt: new Date().toISOString()
                };

                purchases.push(purchase);
                writeJSON(file, purchases);

                audit("PURCHASE_ADD", {
                    purchaseId: purchase.id,
                    supplierId,
                    medicineId,
                    quantity
                });

                return json(res, purchase, 201);
            })
            .catch(error => {
                return json(
                    res,
                    { error: error.message },
                    400
                );
            });

        return;
    }

    // --------------------------------------------------------
    // INVENTORY STOCK-IN
    // --------------------------------------------------------

    if (
        req.method === "POST" &&
        url.pathname === "/api/inventory/stock-in"
    ) {
        readRequestBody(req)
            .then(body => {

                const supplierId = Number(body.supplierId);
                const medicineId = Number(body.medicineId);
                const quantity = Number(body.quantity);
                const unitCost = Number(body.unitCost || 0);

                if (!Number.isInteger(supplierId) || supplierId <= 0) {
                    return json(
                        res,
                        { error: "Valid supplierId is required" },
                        400
                    );
                }

                if (!Number.isInteger(medicineId) || medicineId <= 0) {
                    return json(
                        res,
                        { error: "Valid medicineId is required" },
                        400
                    );
                }

                if (!Number.isFinite(quantity) || quantity <= 0) {
                    return json(
                        res,
                        { error: "Quantity must be greater than zero" },
                        400
                    );
                }

                if (!Number.isFinite(unitCost) || unitCost < 0) {
                    return json(
                        res,
                        { error: "Unit cost cannot be negative" },
                        400
                    );
                }

                const supplierFile =
                    path.join(DATA, "suppliers.json");

                const medicineFile =
                    path.join(DATA, "medicines.json");

                const purchaseFile =
                    path.join(DATA, "purchases.json");

                const suppliers = readJSON(supplierFile);
                const medicines = readJSON(medicineFile);
                const purchases = readJSON(purchaseFile);

                const supplier = suppliers.find(
                    s => Number(s.id) === supplierId
                );

                if (!supplier) {
                    return json(
                        res,
                        { error: "Supplier not found" },
                        404
                    );
                }

                const medicineIndex = medicines.findIndex(
                    m => Number(m.id) === medicineId
                );

                if (medicineIndex === -1) {
                    return json(
                        res,
                        { error: "Medicine not found" },
                        404
                    );
                }

                const medicine = medicines[medicineIndex];

                const oldQuantity =
                    Number(medicine.quantity || 0);

                const newQuantity =
                    oldQuantity + quantity;

                const purchase = {
                    id: nextId(purchases),
                    supplierId,
                    supplierName: supplier.name,
                    medicineId,
                    medicineName: medicine.name,
                    quantity,
                    unitCost,
                    totalCost: quantity * unitCost,
                    date: body.date || new Date().toISOString(),
                    batchNumber: String(body.batchNumber || "").trim(),
                    expiry: String(body.expiry || "").trim(),
                    createdAt: new Date().toISOString()
                };

                medicine.quantity = newQuantity;

                if (purchase.expiry) {
                    medicine.expiry = purchase.expiry;
                }

                purchases.push(purchase);

                writeJSON(purchaseFile, purchases);
                writeJSON(medicineFile, medicines);

                audit("STOCK_IN", {
                    purchaseId: purchase.id,
                    supplierId,
                    supplierName: supplier.name,
                    medicineId,
                    medicineName: medicine.name,
                    quantity,
                    oldQuantity,
                    newQuantity
                });

                return json(
                    res,
                    {
                        success: true,
                        purchase,
                        stock: {
                            medicineId,
                            medicineName: medicine.name,
                            oldQuantity,
                            quantityAdded: quantity,
                            newQuantity
                        }
                    },
                    201
                );
            })
            .catch(error => {
                return json(
                    res,
                    { error: error.message },
                    400
                );
            });

        return;
    }

"""

if marker not in s:
    raise SystemExit("ERROR: CORE API marker not found")

s = s.replace(marker, routes + marker, 1)

p.write_text(s, encoding="utf-8")

print("PASS: Supplier API")
print("PASS: Purchase API")
print("PASS: Stock-In API")
'

echo
echo "[6/7] Syntax and route verification..."

node --check web_server.js

grep -q "/api/suppliers" web_server.js
echo "PASS: /api/suppliers"

grep -q "/api/purchases" web_server.js
echo "PASS: /api/purchases"

grep -q "/api/inventory/stock-in" web_server.js
echo "PASS: /api/inventory/stock-in"

echo
echo "[7/7] Final integrity check..."

python3 -c 'import json; print("Medicines:", len(json.load(open("data/medicines.json"))))'
python3 -c 'import json; print("Suppliers:", len(json.load(open("data/suppliers.json"))))'
python3 -c 'import json; print("Purchases:", len(json.load(open("data/purchases.json"))))'
python3 -c 'import json; print("Audit:", len(json.load(open("data/audit.json"))))'

echo
echo "============================================================"
echo " ONESHOT8 COMPLETE"
echo "============================================================"
echo
echo "New APIs:"
echo "GET  /api/suppliers"
echo "POST /api/suppliers"
echo "GET  /api/purchases"
echo "POST /api/purchases"
echo "POST /api/inventory/stock-in"
echo
echo "V12 remains untouched."
