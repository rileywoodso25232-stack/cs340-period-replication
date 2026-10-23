PYTHON ?= python3

.PHONY: help check environment upstream summary

help:
	@echo "check: validate repository files; environment: record actual environment"
	@echo "upstream: fetch pinned PERIOD source; summary: summarize measured data"

check:
	$(PYTHON) scripts/check_repository.py

environment:
	$(PYTHON) scripts/capture_environment.py

upstream:
	$(PYTHON) scripts/fetch_upstream.py

summary:
	$(PYTHON) scripts/summarize.py
