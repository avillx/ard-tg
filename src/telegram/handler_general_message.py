import logging
from datetime import datetime

import telebot
import telebot.types as telebot_types

import agent
import storage
import telegram.attachments as attachments
import telegram.tools as tools
from telegram import rich_message, sticker_cache
from telegram.chat_event_handler import ChatEventHandler
from telegram.service import Handler
from telegram.typing_action import TypingAction


class GeneralMessageHandler(Handler):
    """
    Handler to process all raw messages to agent
    """

    _agent_service: agent.Service
    _sticker_cache: sticker_cache.StickerCache
    _sticker_pack: str
    _storage: storage.Storage
    _logger: logging.Logger

    def __init__(
        self,
        agent_service: agent.Service,
        sticker_cache: sticker_cache.StickerCache,
        sticker_pack: str,
        storage_: storage.Storage,
        logger: logging.Logger,
    ):
        self._agent_service = agent_service
        self._sticker_cache = sticker_cache
        self._sticker_pack = sticker_pack
        self._storage = storage_
        self._logger = logger.getChild("Telegram.GeneralMessageHandler")

    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(
            self.handle,
            func=lambda message: True,
            pass_bot=True,
        )

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        with TypingAction(bot, message.chat.id, self._logger) as typing_action:
            provided_tools = self._provided_tools(
                chat_id=message.chat.id,
                bot=bot,
            )

            rich_msg = rich_message.RichMessage(
                chat_id=message.chat.id,
                bot=bot,
                draft_id=1,
            )

            ev_handler = ChatEventHandler(
                rich_msg=rich_msg,
                bot=bot,
                typing=typing_action,
            )

            atts = attachments.extract_attachments(
                bot=bot,
                msg=message,
            )

            attachments_info: list[str] = []
            for att in atts:
                try:
                    self._storage.save(att.get_file_name(), att.get_bytes())
                    attachments_info.append(f"attachment tmp/{att.get_file_name()} saved")

                except Exception as e:
                    self._logger.error(f"cant save attachment {e}")
                    attachments_info.append("can't save attachment, gateway problem")

            text_message = represent_message(
                msg=message,
                additional_lines=attachments_info,
            )

            # send request to agent
            try:
                self._agent_service.agent_request(
                    request=text_message,
                    event_handler=ev_handler,
                    provided_tools=provided_tools,
                )

            except Exception as e:
                bot.send_message(message.chat.id, "⚠️ gateway problem")
                self._logger.error(f"gateway exception: {e}")
            finally:
                rich_msg.send_finale()

    # class helper
    def _provided_tools(
        self,
        chat_id: int,
        bot: telebot.TeleBot,
    ) -> list[agent.SafeTool]:

        provided_tools: list[agent.SafeTool] = [
            tools.SendPhotoTool(
                bot=bot,
                chat_id=chat_id,
            ),
            tools.SendFileTool(
                bot=bot,
                chat_id=chat_id,
            ),
            tools.SendVoiceTool(
                bot=bot,
                chat_id=chat_id,
            ),
        ]

        if self._sticker_pack != "":
            provided_tools.append(
                tools.SendStickerTool(
                    bot=bot,
                    chat_id=chat_id,
                    sticker_pack=self._sticker_cache.get_pack(self._sticker_pack),
                )
            )

        return provided_tools


def represent_message(msg: telebot_types.Message, additional_lines: list[str]) -> str:
    current_time = datetime.now().strftime("%y.%m.%d %H:%M")
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
