#!/bin/sh

cd docs/

rm -rf build/
sphinx-build -b linkcheck . build -W
sphinx-build -b html . build -W

