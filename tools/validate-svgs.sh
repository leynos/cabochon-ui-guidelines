#!/usr/bin/env bash
# Validate every SVG as XML, then render a proof sheet and per-figure captures
# with agent-browser. The screenshots are the evidence; do not rely on XML
# validity alone.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="${ROOT}/build"
PROOF="${BUILD}/svg-proof.html"
SHOTS="${BUILD}/figures"
SESSION="cabochon-svg-proof"
STAMP="$(date +%s)"

mkdir -p "${SHOTS}"

python3 -I "${ROOT}/tools/check-figures.py"
python3 -I "${ROOT}/tools/check-figures.py" --self-test

shopt -s nullglob
figures=("${ROOT}"/figures/*.svg)
if (( ${#figures[@]} == 0 )); then
  echo "error: no SVG figures found" >&2
  exit 1
fi

for figure in "${figures[@]}"; do
  xmllint --noout "${figure}"
done
echo "svg: ${#figures[@]} files are well-formed XML"

{
  cat <<'HTML'
<!doctype html>
<html lang="en-GB">
<meta charset="utf-8">
<title>Cabochon SVG proof sheet</title>
<style>
  :root { color-scheme: light; }
  body {
    margin: 0;
    padding: 32px;
    background: #f1eee5;
    color: #17201c;
    font: 14px/1.5 "DejaVu Sans", Arial, sans-serif;
  }
  h1 { font: italic 42px/1.05 Georgia, "DejaVu Serif", serif; margin: 0 0 8px; }
  p.lede { max-width: 70ch; margin: 0 0 32px; color: #59625d; }
  figure {
    margin: 0 0 40px;
    padding: 12px;
    border: 1px solid #17201c;
    background: #faf8f2;
    width: 1120px;
  }
  figcaption {
    display: flex;
    gap: 12px;
    align-items: baseline;
    margin-top: 10px;
    font: 11px/1.5 "DejaVu Sans Mono", monospace;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  figcaption b { color: #8a302f; }
  img { display: block; width: 1096px; height: auto; border: 1px solid #aaa99f; }
</style>
<h1>Cabochon SVG proof sheet</h1>
<p class="lede">Every figure at reading size. Each frame is a separate capture target so detail can be inspected without downsampling.</p>
HTML
  for figure in "${figures[@]}"; do
    name="$(basename "${figure}" .svg)"
    printf '<figure id="fig-%s"><img src="../figures/%s.svg?v=%s" alt="%s"><figcaption><b>%s</b> %s</figcaption></figure>\n' \
      "${name}" "${name}" "${STAMP}" "${name}" "${name}" "${name}"
  done
  cat <<'HTML'
</body>
</html>
HTML
} > "${PROOF}"

agent-browser --session "${SESSION}" open "file://${PROOF}?v=${STAMP}" >/dev/null
agent-browser --session "${SESSION}" wait --load networkidle >/dev/null
agent-browser --session "${SESSION}" screenshot --full "${BUILD}/svg-proof.png" >/dev/null
echo "svg: proof sheet ${BUILD}/svg-proof.png"

for figure in "${figures[@]}"; do
  name="$(basename "${figure}" .svg)"
  page="${BUILD}/capture-${name}.html"
  cat > "${page}" <<HTML
<!doctype html>
<html lang="en-GB">
<meta charset="utf-8">
<title>${name}</title>
<style>
  html, body { margin: 0; padding: 0; background: #f1eee5; }
  img { display: block; width: 1200px; height: auto; }
</style>
<img src="../figures/${name}.svg?v=${STAMP}" alt="${name}">
HTML
  agent-browser --session "${SESSION}" open "file://${page}?v=${STAMP}" >/dev/null
  agent-browser --session "${SESSION}" wait --load networkidle >/dev/null
  agent-browser --session "${SESSION}" screenshot --full "${SHOTS}/${name}.png" >/dev/null
done
echo "svg: ${#figures[@]} per-figure captures in ${SHOTS}"

agent-browser --session "${SESSION}" close >/dev/null
