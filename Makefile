export SHELL := /usr/bin/env TZ=UTC bash -o pipefail

DEBUG ?=
PYPI_ALIAS = $(shell ./plox-common/scripts/misc/get-pypi-pub-target)
PYSRC_DIR = $(CURDIR)
SRC_DIR = plox

export VERSION=$(shell ./plox-common/scripts/get-version)

all: check

include ./plox-common/makefiles/Makefile.python.in

# these targets are declared "phony" so that make won't skip them if a
# file named after the target exists
.PHONY: all $(python-phonies) $(gittooled-phonies)
