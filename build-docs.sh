#!/bin/sh

cd docs/

rm -rf build/

cp -R pytket-docs-theming/_static .
cp -R pytket-docs-theming/quantinuum-sphinx .
cp pytket-docs-theming/conf.py .

sphinx-build -b html . build -W -D html_title="pytket user guide"

# Remove copied files. This ensures reusability.
rm -r _static 
rm -r quantinuum-sphinx
rm conf.py

