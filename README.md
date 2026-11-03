# Association Wiki

A Django-based glossary with fuzzy search and autocomplete functionality. Definitions are stored in `data/definitions.json`.

## Prerequisites

- Docker with Docker Compose, **or** Python 3.12 for running without Docker.

## Running with Docker

From the project's root directory:

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000) to use the glossary.

### Editing the glossary locally

Open **[http://localhost:8000/editor/](http://localhost:8000/editor/)** while Docker Compose is running.

The editor lets you:

- Add a new term and definition.
- Select an existing term to change its name or definition.
- Add or remove optional aliases and related terms.
- Delete terms with confirmation.
- Save directly to `data/definitions.json` (empty `aliases` and `related` fields are omitted).

### To note:
- The editor is intended for local development only. The Docker Compose setup enables it with `DJANGO_DEBUG=true` and `ENABLE_LOCAL_EDITOR=true`, binds port 8000 to **localhost only**, and mounts `./data` as **writable**.
- The editor changes affect your local JSON file only. **Commit and push `data/definitions.json`** to GitHub when ready.
- Changing a term's name updates any other term's `related` references to it; deleting a term removes references to it. The editor also prevents duplicate term names and checks for changes from another session before saving.

## Running without Docker

From the project root, create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Enable the local editor and start Django:

Windows PowerShell:

```powershell
python src/app.py runserver
```

Open `http://localhost:8000/editor/` to execute the local editor or `http://localhost:8000/` to run the glossary.

## Useful information for deployment

- The `Dockerfile` builds the **production** image. It starts Gunicorn, with `DJANGO_DEBUG=false` by default, and does **not** enable the editor.
- `compose.portainer.yaml` is an optional example for the administrator and must be adapted to their hosting setup and image name.
  - The production application must receive a secure `DJANGO_SECRET_KEY` and an appropriate `DJANGO_ALLOWED_HOSTS` value from the server administrator.
  - The application listens on port **8000** inside the container. HTTPS and external access are configured by the administrator.
- **Do not mount `data/` writable in production.** The public glossary is read-only; edited definitions should be committed to GitHub and included in a rebuilt image.
- A GitHub push does not automatically update a running Portainer container. Its image must be rebuilt and redeployed unless an update workflow is configured.