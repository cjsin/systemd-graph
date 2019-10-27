PWD       := $(shell pwd)
SRC       := src
TEST      := test
VENV      := . venv/bin/activate
PYT_FLAGS :=
PYTHON    := $(VENV) && python
PIP       := $(VENV) && pip
PYT_WRAP  := $(VENV) && ./tests-wrapper.sh --top=$(PWD) --src=$(SRC) --path=$(SRC) --path=$(TEST) --mode=path

# the -s flag means disable capture of stdout/stderr. Useful when a test is hanging due to recursion.
#PYT_CAP   := -s
PYT_CAP   :=

PYT       := $(PYT_WRAP) $(PYT_FLAGS) $(PYT_CAP)
SRCS      := $(shell find $(SRC)/ -name "*.py")
TESTS     := $(shell find $(TEST)/ -name "*.py")
PYCACHE   := $(PWD)
TARGETED  := test/test_cycle.py
#export PYTEST_ADDOPTS="-rap"

PYTHONPATH := $(PWD)/src:$(PWD)/test
export PYTHONPATH

# PYTHONBYTECODEPATH doesn't seem to work (or not change where they are generated *to*)
#export PYTHONBYTECODEPATH
#PYTHONBYTECODEPATH := $(PYCACHE)

#PYTHONPYCACHEPREFIX doesn't work until python 3.8
#PYTHONPYCACHEPREFIX := $(PYCACHE)
#export PYTHONPYCACHEPREFIX

PYTHONDONTWRITEBYTECODE=1
export PYTHONDONTWRITEBYTECODE

.PHONY: all test

all: .env test run

.env:
	echo $(PWD)/src:$(PWD)/test > .env

test: $(SOURCES)
	$(PYT) $(TEST)

ttest: $(SOURCES)
	$(PYT) $(TARGETED)

venv:
	python3 -m venv venv

.requirements: venv requirements.txt
	$(PIP) install -r requirements.txt
	touch .requirements

requirements: .requirements

run: .requirements
	$(PYTHON) src/systemd.py
