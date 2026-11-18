from typing import override

import telebot.formatting as fmt
lazy import telebot
lazy import telebot.types as telebot_types

from telegram.service import CallBackQueryHandler, MessageHandler
lazy import agent

ButtonPrefix = "profile"


class ShowProfileHandler(MessageHandler):
    _profile_service: agent.ProfileService

    def __init__(
        self,
        profile_service: agent.ProfileService,
    ):
        self._profile_service = profile_service

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=["profile"], pass_bot=True)

    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:
        markup = telebot_types.InlineKeyboardMarkup()
        btns: list[telebot_types.InlineKeyboardButton] = []
        msg: str = "### Agent profiles:\n"
        for profile_id, profile_description in self._profile_service.all_profiles().items():
            msg += f"- **{profile_id}**: {profile_description}\n"
            data = ":".join([ButtonPrefix, profile_id])
            btns.append(telebot_types.InlineKeyboardButton(profile_id, callback_data=data))

        btns.append(telebot_types.InlineKeyboardButton("default", callback_data=f"{ButtonPrefix}:"))
        _ = markup.add(*btns)

        rich_message = telebot_types.InputRichMessage(markdown=msg)

        _ = bot.send_rich_message(message.chat.id, rich_message, reply_markup=markup)


def is_profile_callback(call: telebot_types.CallbackQuery):
    if not isinstance(call.data, str):
        return None

    return call.data.startswith(ButtonPrefix)


class SetProfileHandler(CallBackQueryHandler):
    """Handle interrupt of the current session and drop it

    Expect call from `/new` command
    """

    _profile_service: agent.ProfileService

    def __init__(
        self,
        profile_service: agent.ProfileService,
    ):
        self._profile_service = profile_service

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_callback_query_handler(
            callback=self.handle,
            func=is_profile_callback,
            pass_bot=True,
        )

    @override
    def handle(self, call: telebot_types.CallbackQuery, bot: telebot.TeleBot) -> None:
        if not isinstance(call.data, str):
            raise ValueError("expected string in callbackdata")

        choice = call.data.split(":", 1)[1]

        try:
            self._profile_service.set_profile(choice)
        except ValueError:
            _ = bot.answer_callback_query(call.id, text=f"Profile is not exist: {choice}")
            return

        _ = bot.answer_callback_query(call.id, text=f"Coosen profile: {choice}")
