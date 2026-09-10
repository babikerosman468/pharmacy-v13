#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/pharmacy-v12"

echo ""
echo "============================================================"
echo " PHARMACY V12 INTERACTIVE CONTROL CENTER"
echo "============================================================"
echo ""
echo "Open:"
echo "http://127.0.0.1:8080"
echo ""
echo "Press Ctrl+C to stop."
echo ""

node web_server.js
