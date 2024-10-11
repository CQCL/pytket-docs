#!/bin/sh
set -e
cd docs/

rm -rf build/

cp -R pytket-docs-theming/_static .
cp -R pytket-docs-theming/quantinuum-sphinx .
cp pytket-docs-theming/conf.py .

# Run link checker in C.I.
sphinx-build -b linkcheck . build -W

set +e

# Build pages
sphinx-build -b html . build -W -D html_title="pytket user guide"

# Remove copied files. This ensures reusability.
rm -r _static 
rm -r quantinuum-sphinx
rm conf.py

