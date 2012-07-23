#!/bin/sh
python setup.py sdist \
  && pushd dist \
  && tar xzvf auto-builder-1.0.tar.gz \
  && pushd auto-builder-1.0 \
  && sudo python setup.py install \
  && popd && popd 

