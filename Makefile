# Pronoun Proofer Zulip Bot

POETRY ?= poetry
VENV_DIR = .venv
PYTHON_VERSION = python3.10

MODEL_WHL = en_coreference_web_trf-3.4.0a2-py3-none-any.whl
ACTIVATE_VENV = source $(VENV_DIR)/bin/activate &&

.PHONY: setup install-model run-prod run-dev tests format clean run_heap_cluster fine_tune_model

all: setup install-model run-prod


# Install Poetry dependencies & set up venv
setup:
	@which poetry > /dev/null || (echo "Poetry not found. Installing..."; curl -sSL https://install.python-poetry.org | $(PYTHON_VERSION) -)
	@$(POETRY) config virtualenvs.in-project true  # Ensure virtualenv is inside project folder
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating..."; \
		$(POETRY) env use $(PYTHON_VERSION); \
		$(POETRY) install --no-root --quiet; \
	fi

# Install spaCy coref model (NLP) from wheel file
install-model:
	@$(ACTIVATE_VENV) python -c "import spacy; spacy.load('en_coreference_web_trf')" 2>/dev/null && echo "Model already installed" || $(POETRY) run pip install $(MODEL_WHL)

# Run bot in prod as 24/7 server to listen & respond 
run-prod:
	@$(ACTIVATE_VENV) $(POETRY) run python bot.py --prod

# Run bot dev script as one-off testing instance
run-dev:
	@$(ACTIVATE_VENV) $(POETRY) run python bot.py --dev

tests:
	@$(ACTIVATE_VENV) @$(POETRY) run pytest tests/

nlp:
	@$(ACTIVATE_VENV) @$(POETRY) run python processing/nlp_coref.py

spacy:
	@$(ACTIVATE_VENV) @$(POETRY) run python processing/nlp_spacy.py

# Auto-format Python code
format:
	@which black > /dev/null || (echo "black not found. Installing..."; $(POETRY) add black)
	$(POETRY) run black bot.py src/

clean:
	@echo "Removing virtual environment..."
	@rm -rf .venv


# Run on heap cluster with pyenv Python 3.10
# NOTE: No longer needed after setup with `systemd` 
#	—> handled by `.service` & `.timer` files
run_heap_cluster:
	@export PYENV_ROOT="$$HOME/.pyenv" && \
	export PATH="$$PYENV_ROOT/bin:$$PATH:~/bin" && \
	eval "$$(pyenv init - bash)" && \
	$(POETRY) run python bot.py


fine_tune_model:
	@$(ACTIVATE_VENV) @$(POETRY) run python train-model/fine_tune_model.py


