#!/data/data/com.termux/files/usr/bin/bash
# compiletex1.sh - Compile LaTeX file using XeLaTeX in Debian via proot

if [ $# -eq 0 ]; then
  echo "❌ Usage: compiletex1.sh <filename.tex>"
  exit 1
fi

TEXFILE=$(realpath "$1")
BASENAME=$(basename "$TEXFILE" .tex)
DIRNAME=$(dirname "$TEXFILE")
PDF="${DIRNAME}/${BASENAME}.pdf"

echo "ℹ️ TEXFILE: $TEXFILE"
echo "ℹ️ DIRNAME: $DIRNAME"
echo "ℹ️ BASENAME: $BASENAME"

run_in_proot() {
  CMD="$1"
  proot-distro login debian -- sh -c "cd \"$DIRNAME\" && $CMD"
}

echo "🔧 Running XeLaTeX (1st pass)..."
run_in_proot "xelatex \"$BASENAME.tex\"" || {
  echo "❌ XeLaTeX failed (1st pass)."
  exit 2
}

if [ -f "${DIRNAME}/${BASENAME}.bcf" ]; then
  echo "📚 Running Biber..."
  run_in_proot "biber \"$BASENAME\""
elif [ -f "${DIRNAME}/${BASENAME}.aux" ]; then
  echo "📚 Running BibTeX..."
  run_in_proot "bibtex \"$BASENAME\""
else
  echo "ℹ️ No Biber or BibTeX files found."
fi

echo "🔧 Running XeLaTeX (2nd pass)..."
run_in_proot "xelatex \"$BASENAME.tex\""

echo "🔧 Running XeLaTeX (final pass)..."
run_in_proot "xelatex \"$BASENAME.tex\""

if [ -f "$PDF" ]; then
  echo "✅ PDF successfully created: $PDF"
  termux-open "$PDF"
else
  echo "❌ PDF not found: $PDF"
  exit 3
fi
