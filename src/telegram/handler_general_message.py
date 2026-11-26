from abc import ABC, abstractmethod
from datetime import datetime
from typing import override
lazy import logging

lazy import telebot
lazy import telebot.types as telebot_types

from agent.chat import Chat, ContentPart, HandlerError, Tool
from agent.tool import ToolExecutor
from telegram.attachments import Attachment, extract_attachments
from telegram.chat_event_handler import TelegramEventHandler
from telegram.rich_message import RichMessage
from telegram.service import MessageHandler
from telegram.typing_action import TypingAction
lazy import storage


class TelegramToolFactory(ABC):
    @abstractmethod
    def get_tools(self,chat_id: int,bot: telebot.TeleBot) -> list[Tool]:
        pass

class GeneralMessageHandler(MessageHandler):
    """Handler to process all raw messages to agent."""
    _chat: Chat
    _tool_factories: list[TelegramToolFactory]
    _storage: storage.Storage
    _tool_executor: ToolExecutor
    _logger: logging.Logger

    def __init__(
        self,
        chat: Chat,
        tool_factories: list[TelegramToolFactory],
        storage_: storage.Storage,
        tool_executor: ToolExecutor,
        logger: logging.Logger,
    ):
        self._chat = chat
        self._tool_factories = tool_factories
        self._tool_executor = tool_executor
        self._storage = storage_
        self._logger = logger.getChild("Telegram.GeneralMessageHandler")

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:

        def allow_all(_message: telebot_types.Message) -> bool:
            return True

        bot.register_message_handler(
            self.handle,
            func=allow_all,
            pass_bot=True,
        )

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        with TypingAction(bot, message.chat.id, self._logger) as typing_action:

            rich_message = RichMessage(
                chat_id=message.chat.id,
                bot=bot,
                draft_id=1,
                logger=self._logger,
            )

            try:
                self._run_chat(rich_message,typing_action,bot,message)

            except HandlerError as err:
                _ = bot.send_message(message.chat.id, "⚠️ gateway problem")
                self._logger.error("gateway handler exception: %s", err)

            except Exception as err:  # noqa: BLE001 - gateway failure must be reported to the user
                _ = bot.send_message(message.chat.id, "⚠️ agent problem")
                self._logger.error("agent exception: %s", err)

            finally:
                rich_message.send_final_message()

    def _run_chat(
        self,
        rich_message: RichMessage,
        typing_action: TypingAction,
        bot: telebot.TeleBot,
        message: telebot_types.Message,
    ):
        provided_tools = self._produce_tools(
            chat_id=message.chat.id,
            bot=bot,
        )

        ev_handler = TelegramEventHandler(
            rich_msg=rich_message,
            tool_executor=self._tool_executor,
            tools=provided_tools,
            typing=typing_action,
        )

        text_message = represent_message(
            msg=message,
            additional_lines=self._resolve_attachments(bot,message),
        )

        request = ContentPart(
            text=text_message,
            image_url="",
        )

        self._chat.chat(
            request=request,
            event_handler=ev_handler,
            provided_tools=provided_tools,
        )

    def _resolve_attachments(self,bot: telebot.TeleBot, message: telebot_types.Message) -> list[str]:
        atts = extract_attachments(
            bot=bot,
            msg=message,
        )
        return self._save_attachments(atts)

    def _save_attachments(self,atts:list[Attachment]) -> list[str]:
        attachments_info: list[str] = []
        for att in atts:
            try:
                self._storage.save(att.get_file_name(), att.get_bytes())
                attachments_info.append(f"attachment tmp/{att.get_file_name()} saved")

            except Exception as e:  # noqa: BLE001 - storage backend is pluggable
                self._logger.error("cant save attachment %s", e)
                attachments_info.append("can't save attachment, gateway problem")
        return attachments_info

    def _produce_tools(self,chat_id: int,bot: telebot.TeleBot) -> list[Tool]:
        tools: list[Tool] = []
        for factory in self._tool_factories:
            factory_tools = factory.get_tools(chat_id,bot)
            tools.extend(factory_tools)
        return tools



def represent_message(msg: telebot_types.Message, additional_lines: list[str]) -> str:
    current_time = datetime.now().astimezone().strftime("%y.%m.%d %H:%M")
    text = f"# From {msg.chat.first_name} ({current_time}):"

    if msg.text is not None:
        text += f"\n{msg.text}"

    if msg.caption is not None:
        text += f"\n{msg.caption}"

    if msg.sticker is not None:
        text += f"\nSticker: {msg.sticker.emoji}"

    for line in additional_lines:
        text += f"\n{line}"

    return text
