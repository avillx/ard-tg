from abc import ABC, abstractmethod
from pathlib import Path
lazy import logging


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
        path = Path(self._storage_path) / file_path

        # save file
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(data)

        self._logger.info("saved %s", path)

    def get(self, file_path: str) -> bytes:
        path = Path(self._storage_path) / file_path

        with path.open("rb") as f:
            data = f.read()

        self._logger.info("readed %s", path)

        return data
