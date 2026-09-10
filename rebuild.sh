cd ~/pharmacy-v12

cp data/medicines.json data/medicines_backup_$(date +%Y%m%d_%H%M%S).json

echo "[]" > data/medicines.json

node app12.js

