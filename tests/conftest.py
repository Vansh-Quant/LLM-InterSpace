import pytest

from interspace.core.config import settings


@pytest.fixture(autouse=True)
def isolated_test_database(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
