# Association Wiki

A Django-based glossary with fuzzy search and autocomplete functionality.

## Prerequisites

- Docker (including Docker Compose)
- Python 3.12 (only required when running without Docker)

## Running with Docker

Open a terminal in the project's root directory and run:

```bash
docker compose up --build
```

Once the container is running, open [http://localhost:8000](http://localhost:8000) in your browser to access the website.

### Note:
- Changes to Python files should trigger Django's automatic reloader.
- Changes to HTML and CSS are visible after refreshing the browser.
- Definitions are loaded from `data/definitions.json` on each search, so updating the JSON file shouldn't need rebuilding the container.
- Definitions should currently be modified manually. I will look at automating this better.

## Running without Docker

From the project's root directory, making the virtual environment (in powershell):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the Django development server:

```bash
python src/app.py runserver
```

The website will be available at [http://localhost:8000](http://localhost:8000).