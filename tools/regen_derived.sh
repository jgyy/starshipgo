#!/bin/bash
# Regenerate every derived file in dependency order (the CI jobs check each of them is up to date):
#   catalog.json (blender/build_all.py) -> specs -> ship.json -> lore/software -> ship spec -> BOM -> drawings -> bug ledger
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python}
$PY tools/specs/gen_specs.py
$PY tools/layout/generate_ship.py
$PY tools/specs/gen_lore.py
$PY tools/specs/gen_software.py
$PY tools/specs/gen_ship_spec.py
$PY tools/layout/bom.py
$PY tools/draft/draft.py --out docs/drafts
$PY tools/docs/bugs_ledger.py
