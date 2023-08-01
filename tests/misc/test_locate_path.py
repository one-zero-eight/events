from pathlib import Path

from src.repositories.predefined.repository import PredefinedRepository


def test_locate_path(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "PREDEFINED_ICS_DIR", Path("some_path"))

    assert PredefinedRepository.locate_ics_by_path("some.ics") == Path("some_path/some.ics")
