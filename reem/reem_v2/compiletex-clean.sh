#!/data/data/com.termux/files/usr/bin/bash
# compiletex-clean.sh - Compile LaTeX file and clean up aux files

if [ $# -eq 0 ]; then
  echo "❌ Usage: compiletex-clean.sh <filename.tex>"
  exit 1
fi

TEXFILE=$(realpath "$1")
BASENAME=$(basename "$TEXFILE" .tex)
DIRNAME=$(dirname "$TEXFILE")
PDF="${DIRNAME}/${BASENAME}.pdf"

if [ ! -x ~/compiletex1.sh ]; then
  echo "❌ Error: ~/compiletex1.sh not found or not executable."
  exit 2
fi

echo "⚙️ Compiling LaTeX file: $TEXFILE"
~/compiletex1.sh "$TEXFILE"

if [ -f "$PDF" ]; then
  echo "✅ PDF successfully compiled: $PDF"
else
  echo "⚠️ Warning: PDF not created. Check LaTeX errors."
fi

echo "🧹 Cleaning auxiliary files..."
EXTS=("aux" "log" "bbl" "blg" "bcf" "run.xml" "out" "toc" "lof" "lot" "fdb_latexmk" "fls" "synctex.gz")

for ext in "${EXTS[@]}"; do
  FILE="${DIRNAME}/${BASENAME}.${ext}"
  if [ -f "$FILE" ]; then
    lsof "$FILE" &>/dev/null
    if [ $? -ne 0 ]; then
      rm -f "$FILE" && echo "🗑️ Deleted: $FILE"
    else
      echo "🔒 Skipped (in use): $FILE"
    fi
  fi
done
