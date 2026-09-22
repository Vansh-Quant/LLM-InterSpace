import os
import subprocess
import sys
from pathlib import Path
from typing import Any

def run_pytest(test_path: str | None = None, timeout_seconds: int = 60) -> dict[str, Any]:
    root = Path.cwd().resolve()
    target = (root / test_path).resolve() if test_path else root
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("Test path must stay inside the project directory") from exc
    if test_path and not (target.name.startswith("test_") or target.parent.name == "tests"):
        raise ValueError("Only pytest test files/directories are allowed")
    timeout_seconds = max(1, min(timeout_seconds, 300))
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(target), "-q"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        shell=False,
    )
    return {
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-6000:],
        "timed_out": False,
    }
