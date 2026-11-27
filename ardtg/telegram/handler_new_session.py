from typing import TYPE_CHECKING, override

from ardtg.telegram.service import CommandPrompter, MessageHandler

if TYPE_CHECKING:
    import telebot
    import telebot.types as telebot_types

    from ardtg.domain.interruption import Interruptor
    from ardtg.domain.session import SessionDropper, SessionSource

_COMMAND = "new"

class NewSessionHandler(MessageHandler,CommandPrompter):
    """Handle interrupt of the current session and drop it

    Expect call from `/new` command
    """

    _interruptor: Interruptor
    _session_dropper: SessionDropper
    _session_source: SessionSource

    def __init__(
        self,
        interruptor: Interruptor,
        session_dropper: SessionDropper,
        session_source: SessionSource
    ):
        self._interruptor = interruptor
        self._session_dropper = session_dropper
        self._session_source = session_source

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "💠 New session"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        session_id = self._session_source.get_session_id()
        self._interruptor.interrupt(session_id)
        self._session_dropper.drop()
        _ = bot.send_message(message.chat.id, "💠 Session cleaned")
