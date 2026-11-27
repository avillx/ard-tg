import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from domain.chat import CompletionEvent, ErrorEvent, Event


class ConsolidationEventHandler(ABC):
    @abstractmethod
    def process_completion(self, event: CompletionEvent):
        pass

    @abstractmethod
    def process_error(self, err: ErrorEvent):
        pass

class ConsolidationEventError(Exception):
    pass

class ConsolidationStreamer(ABC):
    @abstractmethod
    def consolidate(self) -> Iterator[Event]:
        pass

class Consolidator(ABC):
    @abstractmethod
    def consolidate(self,handler: ConsolidationEventHandler):
        pass

class ConsolidationService(Consolidator):
    _consolidation_streamer: ConsolidationStreamer
    _logger: logging.Logger

    def __init__(
        self,
        consolidation_streamer: ConsolidationStreamer,
        logger: logging.Logger,
    ) -> None:
        self._consolidation_streamer = consolidation_streamer
        self._logger=logger.getChild("consolidation")

    @override
    def consolidate(self,handler: ConsolidationEventHandler):
        self._logger.info("consolidation requested")
        for ev in self._consolidation_streamer.consolidate():
            try:
                self._process_event(handler,ev)
            except Exception as e:
                self._logger.error("consolidation event processing failed: %s",e)
                raise ConsolidationEventError() from e

    def _process_event(self,handler: ConsolidationEventHandler,event:Event):
        match event:
            case CompletionEvent():
                handler.process_completion(event)

            case ErrorEvent():
                handler.process_error(event)

            case _:
                raise Exception(f"unexpected event: {type(event)}")
