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

## Useful Information for Deployment
- For local development, run `docker compose up --build`. This builds the image and starts Django with its development server.
- For production deployment, use the `Dockerfile` to build an image that runs the application using Gunicorn.
- The `compose.portainer.yaml` file provides a configuration for deployment through Portainer. Make sure to update the image name and environment variables before deploying.
  - Set `DJANGO_ALLOWED_HOSTS` to the domain or hostname used to access the application, and provide a secure `DJANGO_SECRET_KEY`.
  - The application runs on port `8000` inside the container.
- Definitions are included in the Docker image. Changes to `definitions.json` therefore require rebuilding and redeploying the image.