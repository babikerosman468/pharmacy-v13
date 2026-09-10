#!/data/data/com.termux/files/usr/bin/bash

set -e

cd "$HOME/pharmacy-v13"

echo "============================================================"
echo " PHARMACY MANAGEMENT SYSTEM V13"
echo " ONESHOT9 — STOCK-OUT API"
echo "============================================================"
echo

STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="backups/oneshot9_${STAMP}"

echo "[1/5] Creating backup..."
mkdir -p "$BACKUP"
cp web_server.js "$BACKUP/web_server.js"
cp data/medicines.json "$BACKUP/medicines.json"
cp data/sales.json "$BACKUP/sales.json"
cp data/audit.json "$BACKUP/audit.json"
echo "Backup: $BACKUP"
echo

echo "[2/5] Checking baseline..."
node --check web_server.js
echo "PASS: web_server.js"
echo

echo "[3/5] Installing Stock-Out API..."

if grep -q '/api/inventory/stock-out' web_server.js; then
    echo "Stock-Out API already exists."
else

perl -0pi -e 's#(\s*// --------------------------------------------------------\n\s*// EXISTING / CORE API\n\s*// --------------------------------------------------------)#
    // --------------------------------------------------------
    // INVENTORY STOCK-OUT
    // --------------------------------------------------------

    if (
        req.method === "POST" &&
        url.pathname === "/api/inventory/stock-out"
    ) {
        readRequestBody(req)
            .then(body => {

                const medicineId = Number(body.medicineId);
                const quantity = Number(body.quantity);

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

                const medicineFile =
                    path.join(DATA, "medicines.json");

                const salesFile =
                    path.join(DATA, "sales.json");

                const medicines = readJSON(medicineFile);
                const sales = readJSON(salesFile);

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

                if (oldQuantity < quantity) {
                    return json(
                        res,
                        {
                            error: "Insufficient stock",
                            available: oldQuantity,
                            requested: quantity
                        },
                        400
                    );
                }

                const newQuantity =
                    oldQuantity - quantity;

                const sale = {
                    medicine: medicine.name,
                    qty: quantity,
                    total: quantity * Number(medicine.price || 0),
                    date: body.date || new Date().toISOString()
                };

                medicine.quantity = newQuantity;

                sales.push(sale);

                writeJSON(medicineFile, medicines);
                writeJSON(salesFile, sales);

                audit("STOCK_OUT", {
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
                        sale,
                        stock: {
                            medicineId,
                            medicineName: medicine.name,
                            oldQuantity,
                            quantityRemoved: quantity,
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

\1#' web_server.js

fi

echo "PASS: Stock-Out API"
echo


echo "[4/5] Verifying Stock-Out API..."

grep -q '/api/inventory/stock-out' web_server.js
echo "PASS: Stock-Out route"

grep -q 'STOCK_OUT' web_server.js
echo "PASS: STOCK_OUT audit"

grep -q 'salesFile' web_server.js
echo "PASS: sales.json integration"

echo
echo "[5/5] Final syntax check..."

node --check web_server.js

echo "PASS: web_server.js syntax"
echo
echo "============================================================"
echo " ONESHOT9 COMPLETE"
echo " Stock-Out API installed successfully."
echo " V12 remains untouched."
echo "============================================================"
