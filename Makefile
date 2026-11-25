.PHONY: help figures figures-check validate-svg check-fmt fmt markdownlint spelling python-lint python-typecheck python-test links states keyboard layout requirements check all

SHELL := bash
PYTHON ?= python3
UV ?= uv
MDLINT ?= markdownlint-cli2
MDTABLEFIX ?= mdtablefix
TYPOS_CONFIG_BUILDER_VERSION ?= v0.1.4
TYPOS_CONFIG_BUILDER = $(UV) tool run --python 3.14 --from \
	"git+https://github.com/leynos/typos-config-builder.git@$(TYPOS_CONFIG_BUILDER_VERSION)" \
	typos-config-builder

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

figures: ## Regenerate every SVG figure from tools/make-figures.py
	$(PYTHON) -I tools/make-figures.py

figures-check: ## Check every figure against its declared class and geometry
	$(PYTHON) -I tools/check-figures.py
	$(PYTHON) -I tools/check-figures.py --self-test

validate-svg: figures ## Validate SVG XML and render a proof sheet with agent-browser
	bash tools/validate-svgs.sh
	git diff --exit-code HEAD -- figures

check-fmt: ## Check Markdown table and paragraph formatting
	$(MDTABLEFIX) --git --include-untracked --check

fmt: ## Format Markdown tables and wrap prose
	$(MDTABLEFIX) --git --include-untracked --in-place --wrap --renumber --breaks --ellipsis --fences

markdownlint: ## Lint Markdown
	$(MDLINT) "*.md" "book/**/*.md" "docs/**/*.md"

spelling: ## Enforce en-GB-oxendict spelling
	$(TYPOS_CONFIG_BUILDER) gate --repository .

python-lint: ## Lint the Python tools with ruff, interrogate and pylint
	$(UV) run ruff check tools
	$(UV) run interrogate tools
	$(UV) run pylint tools

python-typecheck: ## Type-check the Python tools with ty
	$(UV) run ty check tools

python-test: ## Run the property tests
	$(UV) run pytest

links: ## Check links, anchors and the structural contract
	$(PYTHON) -I tools/check-links.py
	$(PYTHON) -I tools/check-links.py --self-test

states: ## Check the live-state projection, transitions and event fixtures
	$(PYTHON) -I tools/check-states.py
	$(PYTHON) -I tools/check-states.py --self-test

keyboard: ## Check the declared Escape routing order
	$(PYTHON) -I tools/check-keyboard.py
	$(PYTHON) -I tools/check-keyboard.py --self-test

layout: ## Derive and check the layout budgets from declared tokens
	$(PYTHON) -I tools/check-layout.py
	$(PYTHON) -I tools/check-layout.py --self-test

requirements: ## Check the structured requirement registry against the checklist
	$(PYTHON) -I tools/check-requirements.py
	$(PYTHON) -I tools/check-requirements.py --self-test

check: check-fmt markdownlint spelling python-lint python-typecheck python-test figures-check links states keyboard layout requirements validate-svg ## Run every gate
	@echo "All gates passed."

all: check ## Compatibility alias for check
