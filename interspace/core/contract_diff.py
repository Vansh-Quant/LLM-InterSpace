from typing import Any


def _walk(value: Any, path: str = "") -> dict[str, Any]:
    """Flatten JSON-like data into deterministic path -> value entries."""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key in sorted(value):
            child_path = f"{path}.{key}" if path else key
            result.update(_walk(value[key], child_path))
        return result
    if isinstance(value, list):
        result: dict[str, Any] = {}
        for index, item in enumerate(value):
            child_path = f"{path}[{index}]"
            result.update(_walk(item, child_path))
        return result
    return {path: value}


def diff_contracts(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    """Return deterministic added/removed/changed JSON paths."""
    before_flat = _walk(before)
    after_flat = _walk(after)

    before_paths = set(before_flat)
    after_paths = set(after_flat)

    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    changed = sorted(
        path
        for path in before_paths & after_paths
        if before_flat[path] != after_flat[path]
    )

    return {"added": added, "removed": removed, "changed": changed}
