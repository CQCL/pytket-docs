#!/bin/sh

cd docs/

rm -rf build/
sphinx-build -b html . build

