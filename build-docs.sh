#!/bin/sh

cd docs/

rm -rf build/

# Run link checker in C.I.
sphinx-build -b linkcheck . build -W
# Build pages
sphinx-build -b html . build -W

