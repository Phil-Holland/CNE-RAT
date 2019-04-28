#!/bin/bash

# this script uses jsonschema2md to create markdown
# files for any schemas in the ../schemas directory

jsonschema2md -d ../schemas -o . -x - -n