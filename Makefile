.PHONY: help figures validate-svg check-fmt fmt markdownlint spelling links states check all

SHELL := bash
PYTHON ?= python3
MDLINT ?= markdownlint-cli2
MDTABLEFIX ?= mdtablefix
TYPOS ?= typos

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

figures: ## Regenerate every SVG figure from tools/make-figures.py
	$(PYTHON) -I tools/make-figures.py

validate-svg: figures ## Validate SVG XML and render a proof sheet with agent-browser
	bash tools/validate-svgs.sh

check-fmt: ## Check Markdown table and paragraph formatting
	$(MDTABLEFIX) --git --include-untracked --check

fmt: ## Format Markdown tables and wrap prose
	$(MDTABLEFIX) --git --include-untracked --in-place --wrap --renumber --breaks --ellipsis --fences

markdownlint: ## Lint Markdown
	$(MDLINT) "*.md" "book/**/*.md"

spelling: ## Check spelling with typos
	$(TYPOS)

links: ## Check links, anchors and the structural contract
	$(PYTHON) -I tools/check-links.py
	$(PYTHON) -I tools/check-links.py --self-test

states: ## Check the live-state projection, transitions and event fixtures
	$(PYTHON) -I tools/check-states.py
	$(PYTHON) -I tools/check-states.py --self-test

check: check-fmt markdownlint spelling links states validate-svg ## Run every gate
	@echo "All gates passed."

all: check ## Compatibility alias for check
