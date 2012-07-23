#!/bin/sh
python manifest_test.py && \
python auto_builder_test.py && \
python generator_test.py && \
python dependencies_test.py 
