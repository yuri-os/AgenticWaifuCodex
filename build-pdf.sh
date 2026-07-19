#!/usr/bin/env bash
# Build the whole book into a single PDF for review.
#   ./build-pdf.sh            -> dist/agentic-waifu-codex.pdf
#   ./build-pdf.sh out.pdf    -> custom output path
#
# Requires: pandoc + weasyprint (pip install weasyprint).
# Chapters then appendices, concatenated in filename order (zero-padded => reading order).
set -euo pipefail
cd "$(dirname "$0")"

OUT="${1:-dist/agentic-waifu-codex.pdf}"
mkdir -p "$(dirname "$OUT")"

# shellcheck disable=SC2086
pandoc chapters/*.md appendices/*.md \
  --standalone \
  --toc --toc-depth=2 \
  --metadata title="The Agentic Waifu Codex" \
  --metadata subtitle="YuriOS Lab · The Codex · Vol. I" \
  --metadata author="The Operator" \
  --metadata date="$(date +%Y-%m-%d)" \
  --pdf-engine=weasyprint \
  --css pdf/style.css \
  -o "$OUT"

echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
