.PHONY: install data run test lint clean

# Uses uv (one venv per project). Fallbacks to plain python if uv is absent.
RUN := $(shell command -v uv >/dev/null 2>&1 && echo "uv run" || echo "python -m")

install:            ## create the environment and install dependencies
	uv sync --extra dev

data:               ## refresh the dated Eurostat snapshot in data/
	uv run python scripts/download_data.py

run:                ## launch the Streamlit app
	uv run streamlit run app.py

test:               ## run the targeted test suite
	uv run pytest -q

clean:              ## remove caches
	rm -rf .pytest_cache **/__pycache__ .streamlit/cache
