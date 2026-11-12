"""adapter to generated agent api"""

from .event import ConsolidationEventHandler, EventHandler
from .service import Service
from .session import SessionService, SuperfluousSetSessionError, SystemTime
from .tool import SafeTool
