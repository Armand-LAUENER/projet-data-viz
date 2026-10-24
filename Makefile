.PHONY: install data tables run test lint clean

install:            ## create the environment and install dependencies
	uv sync --extra dev

data:               ## download the raw BAAC CSVs into data/raw/ (+ MANIFEST)
	uv run python scripts/download_data.py

tables:             ## build the aggregated Parquet tables in data/processed/
	uv run python scripts/build_tables.py

run:                ## launch the Streamlit app
	uv run streamlit run app.py

test:               ## run the targeted test suite
	uv run pytest -q

lint:               ## static checks
	uvx ruff check .

clean:              ## remove caches
	rm -rf .pytest_cache .ruff_cache **/__pycache__
