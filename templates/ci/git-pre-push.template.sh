#!/bin/sh
# k-method Local Git Pre-Push Quality Gate Hook
# Install into your local repository by copying to: .git/hooks/pre-push
# (Ensure executable permissions on Unix: chmod +x .git/hooks/pre-push)

set -e

echo "═════════════════════════════════════════════════════════"
echo "  [k-method] Ejecutando Quality Gates antes del push... "
echo "═════════════════════════════════════════════════════════"

# Execute universal verification runner
python scripts/verify-all.py

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Las compuertas de calidad fallaron. Git push abortado."
    exit 1
fi

echo "✅ Quality Gates superados. Procediendo con el push."
exit 0
