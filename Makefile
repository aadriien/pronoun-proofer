# Pronoun Proofer Zulip Bot

POETRY ?= poetry
VENV_DIR = .venv
PYTHON_VERSION = python3.10

MODEL_WHL = en_coreference_web_trf-3.4.0a2-py3-none-any.whl
ACTIVATE_VENV = source $(VENV_DIR)/bin/activate &&

.PHONY: setup install-model run-prod run-dev tests format clean run_heap_cluster fine_tune_model

all: setup run-prod


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

# Run bot in prod as 24/7 service to listen & respond 
run-prod: install-model
	@$(ACTIVATE_VENV) $(POETRY) run python bot.py --prod

# Run bot dev script as one-off testing instance
run-dev: install-model
	@$(ACTIVATE_VENV) $(POETRY) run python bot.py --dev

tests: install-model
	@$(ACTIVATE_VENV) $(POETRY) run pytest tests/

nlp: install-model
	@$(ACTIVATE_VENV) $(POETRY) run python processing/nlp_coref.py

spacy: install-model
	@$(ACTIVATE_VENV) $(POETRY) run python processing/nlp_spacy.py

# Auto-format Python code
format:
	@which black > /dev/null || (echo "black not found. Installing..."; $(POETRY) add black)
	$(POETRY) run black bot.py src/

clean:
	@echo "Removing virtual environment..."
	@rm -rf .venv


# Run on heap cluster with pyenv Python 3.10
# Command referenced in `.service` file (called upon by `systemd`)
#	—> daily logs handled by `.service` & `.timer` files
run_heap_cluster:
	@export PYENV_ROOT="$$HOME/.pyenv" && \
	export PATH="$$PYENV_ROOT/bin:$$PATH:~/bin" && \
	eval "$$(pyenv init - bash)" && \
	$(POETRY) run python bot.py --prod


fine_tune_model: install-model
	@$(ACTIVATE_VENV) $(POETRY) run python train-model/fine_tune_model.py


