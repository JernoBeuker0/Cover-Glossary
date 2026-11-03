"""Local-only JSON glossary editor. Routes are registered only in debug + opt-in mode."""
import hashlib
import json
import os
import tempfile
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from search import DATA_FILE


class EditorError(ValueError):
    pass


def read_glossary(path=DATA_FILE):
    path = Path(path)
    raw = path.read_bytes()
    entries = json.loads(raw)
    if not isinstance(entries, dict):
        raise EditorError("The glossary must be a JSON object.")
    return entries, hashlib.sha256(raw).hexdigest()


def _items(values, label, limit=30):
    if not isinstance(values, list) or len(values) > limit:
        raise EditorError(f"{label} must be a list of at most {limit} items.")
    result = []
    seen = set()
    for item in values:
        if not isinstance(item, str):
            raise EditorError(f"{label} must only contain text.")
        item = item.strip()
        if len(item) > 120:
            raise EditorError(f"{label} values cannot exceed 120 characters.")
        if item and item.casefold() not in seen:
            result.append(item)
            seen.add(item.casefold())
    return result


def update_entry(entries, old_name, term, definition, aliases, related):
    """Return a modified copy. Preserve unrelated entries and optional fields."""
    if not isinstance(old_name, str) or not isinstance(term, str) or not isinstance(definition, str):
        raise EditorError("Term and definition must be text.")
    term, definition = term.strip(), definition.strip()
    if not term or len(term) > 120 or not definition or len(definition) > 4000:
        raise EditorError("Enter a term (up to 120 characters) and a definition (up to 4000).")
    if old_name and old_name not in entries:
        raise EditorError("The term you are editing no longer exists. Refresh and try again.")
    if any(word.casefold() == term.casefold() and word != old_name for word in entries):
        raise EditorError("A term with this name already exists.")

    aliases = _items(aliases, "Aliases")
    related = _items(related, "Related terms")
    if term.casefold() in {value.casefold() for value in aliases}:
        aliases = [value for value in aliases if value.casefold() != term.casefold()]

    # Allow choosing the old name while renaming, but prohibit self-links.
    related = [term if old_name and r == old_name else r for r in related]
    if any(r == term for r in related):
        related = [r for r in related if r != term]
    valid_terms = set(entries) - ({old_name} if old_name else set())
    if old_name:
        valid_terms.add(term)
    if any(r not in valid_terms for r in related):
        raise EditorError("Related terms must refer to existing glossary terms.")

    updated = {}
    new_info = {"definition": definition}
    if aliases:
        new_info["aliases"] = aliases
    if related:
        new_info["related"] = related

    for word, info in entries.items():
        if word == old_name:
            updated[term] = new_info
        else:
            updated[word] = dict(info)
    if not old_name:
        updated[term] = new_info

    if old_name and old_name != term:
        for word, info in updated.items():
            if word != term and "related" in info:
                info["related"] = [term if item == old_name else item for item in info["related"]]
    return updated


def remove_entry(entries, term):
    if not isinstance(term, str) or term not in entries:
        raise EditorError("That term no longer exists.")
    updated = {}
    for word, info in entries.items():
        if word == term:
            continue
        info = dict(info)
        if "related" in info:
            related = [other for other in info["related"] if other != term]
            if related:
                info["related"] = related
            else:
                info.pop("related")
        updated[word] = info
    return updated


def write_glossary(entries, version, path=DATA_FILE):
    """Refuse stale updates; atomically replace JSON to avoid partial writes."""
    path = Path(path)
    if not isinstance(version, str) or version != hashlib.sha256(path.read_bytes()).hexdigest():
        raise EditorError("The glossary changed since you opened it. Reload before saving.")
    serialized = json.dumps(entries, ensure_ascii=False, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=".definitions-", suffix=".tmp",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@require_GET
def editor_page(request):
    return render(request, "editor.html")


@require_GET
def editor_data(request):
    entries, version = read_glossary()
    return JsonResponse({"entries": entries, "version": version})


def _body(request):
    try:
        result = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise EditorError("Invalid JSON request.")
    if not isinstance(result, dict):
        raise EditorError("Invalid submission.")
    return result


@require_POST
def editor_save(request):
    try:
        payload = _body(request)
        entries, current = read_glossary()
        if payload.get("version") != current:
            raise EditorError("The glossary changed. Reload before saving.")
        updated = update_entry(entries, payload.get("original", ""), payload.get("term"),
                               payload.get("definition"), payload.get("aliases", []),
                               payload.get("related", []))
        version = write_glossary(updated, current)
        return JsonResponse({"entries": updated, "version": version})
    except (EditorError, OSError) as exc:
        return JsonResponse({"error": str(exc)}, status=409 if "changed" in str(exc).lower() else 400)


@require_POST
def editor_delete(request):
    try:
        payload = _body(request)
        entries, current = read_glossary()
        if payload.get("version") != current:
            raise EditorError("The glossary changed. Reload before deleting.")
        updated = remove_entry(entries, payload.get("term"))
        version = write_glossary(updated, current)
        return JsonResponse({"entries": updated, "version": version})
    except (EditorError, OSError) as exc:
        return JsonResponse({"error": str(exc)}, status=409 if "changed" in str(exc).lower() else 400)
