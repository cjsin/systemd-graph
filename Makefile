PWD       := $(shell pwd)
SRC       := src
TEST      := test
PYT_FLAGS :=
USE_VENV  := no
# the -s flag means disable capture of stdout/stderr. Useful when a test is hanging due to recursion.
#PYT_CAP   := -s
PYT_CAP   :=
SRCS      := $(shell find $(SRC)/ -name "*.py")
TESTS     := $(shell find $(TEST)/ -name "*.py")
PYCACHE   := $(PWD)
TEST_TGT  := test/test_attrdict.py
RUN_TGT   := src/main.py
#export PYTEST_ADDOPTS="-rap"

ifeq ($(USE_VENV),yes)
VENV      := . venv/bin/activate
PYTHON    := $(VENV) && python
PIP       := $(VENV) && pip
PYT_WRAP  := $(VENV) && ./tests-wrapper.sh --top=$(PWD) --src=$(SRC) --path=$(SRC) --path=$(TEST) --mode=path
RUN_REQS  := .requirements
else
PYTHON    := python3
PIP       := pip3 --user
PYT_WRAP  := ./tests-wrapper.sh --top=$(PWD) --src=$(SRC) --path=$(SRC) --path=$(TEST) --mode=path
RUN_REQS  :=
endif

PYT       := $(PYT_WRAP) $(PYT_FLAGS) $(PYT_CAP)

export PYTHONPATH               := $(PWD)/src:$(PWD)/test
export PYTHONDONTWRITEBYTECODE  := 1

# PYTHONBYTECODEPATH doesn't seem to work (or not change where they are generated *to*)
#export PYTHONBYTECODEPATH := $(PYCACHE)

#PYTHONPYCACHEPREFIX doesn't work until python 3.8
#export PYTHONPYCACHEPREFIX := $(PYCACHE)


.PHONY: all test

all: .env test run

.env:
	@echo "PYTHONPATH='$(PYTHONPATH)'" > .env

test: $(SOURCES)
	@$(PYT) $(TEST)

ttest: $(SOURCES)
	@$(PYT) $(TEST_TGT)

venv:
	python3 -m venv venv

.requirements: venv requirements.txt
	$(PIP) install -r requirements.txt
	touch .requirements

requirements: .requirements

r: $(RUN_REQS)
	@$(PYTHON) $(RUN_TGT)

dot: $(RUN_REQS)
	@$(PYTHON) $(RUN_TGT) > test.dot
	xdot test.dot < /dev/null > /dev/null 2>&1 &

electron:
	npm install electron

eapp:
	cd app/eapp
	npm install node-static


setup: electron eapp

