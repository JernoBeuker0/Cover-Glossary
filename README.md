# Association Wiki

A Django-based glossary with fuzzy search and autocomplete functionality. Definitions are stored in `data/definitions.json`.

## Prerequisites

- Docker with Docker Compose

## Running with Docker

From the project's root directory:

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000) to use the glossary.

## Editing the glossary locally

Open **[http://localhost:8000/editor/](http://localhost:8000/editor/)** while Docker Compose is running.

The editor lets you:

- Add a new term and definition.
- Select an existing term to change its name, definition, aliases, or related terms.
- Delete terms with confirmation.
- Save directly to `data/definitions.json`.

### To note:
- The editor is intended for local development only. The Docker Compose setup enables it with `DJANGO_DEBUG=true` and `ENABLE_LOCAL_EDITOR=true`, binds port 8000 to **localhost only**, and mounts `./data` as **writable**.
- The editor changes affect your local JSON file only. **Commit and push `data/definitions.json`** to GitHub when ready.
- Changing a term's name updates any other term's `related` references to it; deleting a term removes references to it. The editor also prevents duplicate term names and checks for changes from another session before saving.

## Useful information for deployment
- This application runs both locally and in production.
- `compose.portainer.yaml` is an example how to run in production and must be adapted.
- Do not mount `data/` writable in production. The public glossary is read-only; edited definitions should be committed to GitHub and included in a rebuilt image.
- A GitHub push does not automatically update a running Portainer container. Its image must be rebuilt and redeployed unless there is an automatic rebuild configured (not as far as I know).