#!/bin/bash
# .skill arşivini source/ dizininden yeniden oluşturur.
# Çalıştır: ./build.sh
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d source/turkce-imla-anlatim ]; then
  echo "HATA: source/turkce-imla-anlatim bulunamadı" >&2
  exit 1
fi

rm -f turkce-imla-anlatim.skill

cd source
zip -r ../turkce-imla-anlatim.skill turkce-imla-anlatim \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*/test_*.py"

echo "Oluşturuldu: turkce-imla-anlatim.skill"
