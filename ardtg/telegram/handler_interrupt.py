from typing import TYPE_CHECKING, override

from ardtg.telegram.service import CommandPrompter, MessageHandler

if TYPE_CHECKING:
    import telebot
    import telebot.types as telebot_types

    from ardtg.domain.interruption import Interruptor
    from ardtg.domain.session import SessionSource

_COMMAND = "interrupt"

class InterruptHandler(MessageHandler,CommandPrompter):
    """Handle interrupt of the agent stream

    Expect call from `/interrupt` command
    """

    _interruptor: Interruptor
    _session_source: SessionSource

    def __init__(self, interruptor: Interruptor, session_source: SessionSource):
        self._interruptor = interruptor
        self._session_source = session_source

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "🚧 Interrupt agent response"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        session_id = self._session_source.get_session_id()
        self._interruptor.interrupt(session_id)
        _ = bot.send_message(message.chat.id, "🚧 Interrupting agent")
