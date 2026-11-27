from typing import TYPE_CHECKING, override

import telebot.types as telebot_types

from ardtg.telegram.service import CallBackQueryHandler, CommandPrompter, MessageHandler

if TYPE_CHECKING:
    import telebot

    from ardtg.domain.profile import ProfileRepo, ProfileSetter

BUTTON_PREFIX = "profile"
_COMMAND = "profile"


class ShowProfileHandler(MessageHandler,CommandPrompter):
    _profile_source: ProfileRepo

    def __init__(self, profile_source: ProfileRepo):
        self._profile_source = profile_source

    @override
    def command_prompt(self) -> tuple[str,str]:
        return _COMMAND, "👤 Show agent profiles"

    @override
    def register_on(self, bot: telebot.TeleBot) -> None:
        bot.register_message_handler(self.handle, commands=[_COMMAND], pass_bot=True)

    @override
    def handle(self, message: telebot_types.Message, bot: telebot.TeleBot) -> None:

        markup = telebot_types.InlineKeyboardMarkup(row_width=1)
        btns: list[telebot_types.InlineKeyboardButton] = []
        msg: str = "### 👤 Agent profiles:\n"
        for profile in self._profile_source.all_profiles():
            msg += f"- **{profile.name}**: {profile.description}\n"
            data = ":".join([BUTTON_PREFIX, profile.name])
            btns.append(telebot_types.InlineKeyboardButton(
                text=profile.name,
                callback_data=data,
            ))

        btns.append(telebot_types.InlineKeyboardButton("default", callback_data=f"{BUTTON_PREFIX}:"))
        _ = markup.add(*btns)

        rich_message = telebot_types.InputRichMessage(markdown=msg)

        _ = bot.send_rich_message(message.chat.id, rich_message, reply_markup=markup)



def is_profile_callback(call: telebot_types.CallbackQuery):
    if not isinstance(call.data, str):
        return None

    return call.data.startswith(BUTTON_PREFIX)


class SetProfileHandler(CallBackQueryHandler):
    """Handle interrupt of the current session and drop it

    Expect call from `/new` command
    """

    _profile_setter: ProfileSetter

    def __init__(
        self,
        profile_setter: ProfileSetter,
    ):
        self._profile_setter = profile_setter

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
            self._profile_setter.set_profile(choice)
        except ValueError:
            _ = bot.answer_callback_query(
                callback_query_id = call.id,
                text=f"Profile is not exist: {choice}"
            )
        else:
            _ = bot.answer_callback_query(
                callback_query_id = call.id,
                text=f"Coosen profile: {choice}",
            )

        chat_id = resolve_chat_id(call)
        message_id = resolve_message_id(call)
        if chat_id is None or message_id is None:
            return

        _ = bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

def resolve_message_id(q: telebot_types.CallbackQuery) -> int | None:
    if not isinstance(q.message, telebot_types.MaybeInaccessibleMessage):
       return None

    if not isinstance(q.message.id, int):
       return None

    return q.message.id

def resolve_chat_id(q: telebot_types.CallbackQuery) -> int | None:
    if not isinstance(q.message, telebot_types.MaybeInaccessibleMessage):
       return None

    return q.message.chat.id
