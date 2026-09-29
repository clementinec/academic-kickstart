#!/bin/sh
# Build both documents from shared content; keep TeX intermediates out of the repo.
set -eu

cv_repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cv_build_dir=$(mktemp -d "${TMPDIR:-/tmp}/forge-cv.XXXXXX")
trap 'rm -rf "$cv_build_dir"' EXIT HUP INT TERM
cd "$cv_repo_root"

for cv_document in cv cv-profile; do
  if ! latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -outdir="$cv_build_dir" "$cv_document.tex" > "$cv_build_dir/$cv_document-build.log" 2>&1; then
    cat "$cv_build_dir/$cv_document-build.log" >&2
    exit 1
  fi
done

python3 - "$cv_build_dir" <<'PY'
from pathlib import Path
import re
import sys

build = Path(sys.argv[1])
for name in ('cv', 'cv-profile'):
    log = (build / f'{name}.log').read_text()
    if re.search(r'Overfull \\[hv]box', log):
        raise SystemExit(f'{name}: layout overflow; inspect the LaTeX source before publishing.')
PY

cp "$cv_build_dir/cv.pdf" cv.pdf
cp "$cv_build_dir/cv.pdf" public/cv.pdf
cp "$cv_build_dir/cv.pdf" static/files/cv.pdf
cp "$cv_build_dir/cv-profile.pdf" public/cv-profile.pdf

if command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -f 1 -l 1 -singlefile -scale-to 1800 -png \
    "$cv_build_dir/cv.pdf" public/images/cv-preview
fi

printf '%s\n' 'Built full CV, short profile, and available preview; public downloads are synchronized.'
