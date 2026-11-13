import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path


class Storage(ABC):
    @abstractmethod
    def save(self, file_path: str, data: bytes):
        pass

    @abstractmethod
    def get(self, file_path: str) -> bytes:
        pass


class FileStorage(Storage):
    _storage_path: str
    _logger: logging.Logger

    def __init__(
        self,
        storage_path: str,
        logger: logging.Logger,
    ) -> None:
        super().__init__()
        self._storage_path = storage_path
        self._logger = logger.getChild("files")

    def save(self, file_path: str, data: bytes):
        absolute_string = os.path.join(self._storage_path, file_path)

        # save file
        path = Path(absolute_string)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(data)

        self._logger.info(f"saved {absolute_string}")

    def get(self, file_path: str) -> bytes:
        absolute_string = os.path.join(self._storage_path, file_path)

        with open(absolute_string, "rb") as f:
            data = f.read()

        self._logger.info(f"readed {absolute_string}")

        return data
