#!/data/data/com.termux/files/usr/bin/bash

echo "Stopping Pharmacy System..."

# kill all node processes safely
pkill -f "node"

# free dashboard port (important)
fuser -k 8080/tcp 2>/dev/null

echo "All servers stopped."


