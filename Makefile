# Pronoun Proofer Zulip Bot

POETRY ?= poetry
VENV_DIR = .venv
PYTHON_VERSION = python3

.PHONY: setup run tests format clean run_heap_cluster fine_tune_model 

all: setup run 

# Install Poetry dependencies & set up venv
setup:
	@which poetry > /dev/null || (echo "Poetry not found. Installing..."; curl -sSL https://install.python-poetry.org | $(PYTHON_VERSION) -)
	@$(POETRY) config virtualenvs.in-project true  # Ensure virtualenv is inside project folder
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating..."; \
		$(POETRY) env use $(PYTHON_VERSION); \
		$(POETRY) install --no-root --quiet; \
	fi

run: 
	@$(POETRY) run python bot.py

tests:
	@$(POETRY) run pytest tests/

nlp:
	@$(POETRY) run python processing/nlp_coref.py

spacy:
	@$(POETRY) run python processing/nlp_spacy.py

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
	@$(POETRY) run python train-model/fine_tune_model.py


