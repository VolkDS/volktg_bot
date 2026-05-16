#!/bin/bash

docker build --no-cache --progress=plain -t test/volktg_bot --build-arg PY_BUILD_VERSION=1.1.0 .
