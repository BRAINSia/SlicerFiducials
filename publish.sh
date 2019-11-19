#!/usr/bin/env bash
# Author: "abpwrs"
# Date: 20191115


# script:
rm -rf ./build ./dist
python setup.py sdist bdist_wheel
twine upload dist/*

