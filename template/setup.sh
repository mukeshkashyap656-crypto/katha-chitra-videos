#!/bin/bash
# Katha Chitra Ramayan video template setup (free tools only). Usage: bash setup.sh /home/claude/ep
set -e
EP=${1:-/home/claude/ep}; T=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$EP/proj/assets" "$EP/proj/cover/assets" "$EP/proj/cover/fonts/@fontsource/mukta/files" "$EP/proj/cover/fonts/@fontsource/rozha-one/files" "$EP/proj/cover/fonts/gsap/dist"
pip install --break-system-packages -q pycairo numpy pillow 2>/dev/null || true
cd "$EP/proj" && [ -f package.json ] || npm init -y >/dev/null
npm i -s hyperframes gsap @fontsource/mukta @fontsource/rozha-one >/dev/null 2>&1
npx hyperframes telemetry disable >/dev/null 2>&1 || true
cp "$T"/assets/* "$EP/proj/assets/"
cp node_modules/@fontsource/mukta/files/mukta-devanagari-800-normal.woff2 cover/fonts/@fontsource/mukta/files/
cp node_modules/@fontsource/rozha-one/files/rozha-one-devanagari-400-normal.woff2 cover/fonts/@fontsource/rozha-one/files/
cp node_modules/gsap/dist/gsap.min.js cover/fonts/gsap/dist/
cp "$T"/assets/{frame_b3.png,katha_chitra_logo.png} cover/assets/
echo "ready: $EP/proj  (lint: npx hyperframes lint . | render: npx hyperframes render . -q delivery -o out.mp4)"
