# Pronoun Proofer Zulip Bot

POETRY = poetry
VENV_DIR = .venv
PYTHON_VERSION = python3.10

.PHONY: setup run tests format clean 

all: setup run 

# Install Poetry dependencies & set up venv
setup:
	@which poetry > /dev/null || (echo "Poetry not found. Installing..."; curl -sSL https://install.python-poetry.org | python3 -)
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
	@$(POETRY) run python src/nlp_coref.py

spacy:
	@$(POETRY) run python src/nlp_spacy.py

# Auto-format Python code
format:
	@which black > /dev/null || (echo "black not found. Installing..."; $(POETRY) add black)
	$(POETRY) run black bot.py src/

clean:
	@echo "Removing virtual environment..."
	@rm -rf .venv

