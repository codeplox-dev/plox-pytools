#!/bin/bash

set -euo pipefail

eval "$(direnv export bash)"
direnv allow .
eval "$(direnv export bash)"
make install-deps
