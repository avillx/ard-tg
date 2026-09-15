import logging
from pathlib import Path

import pytest

from storage import FileStorage


def test_save_creates_parent_dirs_and_writes_bytes(tmp_path: Path, logger: logging.Logger) -> None:
    storage = FileStorage(storage_path=str(tmp_path), logger=logger)

    storage.save("nested/dir/file.bin", b"data")

    assert (tmp_path / "nested" / "dir" / "file.bin").read_bytes() == b"data"


def test_get_returns_saved_bytes(tmp_path: Path, logger: logging.Logger) -> None:
    storage = FileStorage(storage_path=str(tmp_path), logger=logger)
    storage.save("file.bin", b"hello")

    assert storage.get("file.bin") == b"hello"


def test_get_missing_file_raises(tmp_path: Path, logger: logging.Logger) -> None:
    storage = FileStorage(storage_path=str(tmp_path), logger=logger)

    with pytest.raises(FileNotFoundError):
        storage.get("missing.bin")
