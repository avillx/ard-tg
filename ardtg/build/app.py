import secrets
import signal
import threading
from typing import TYPE_CHECKING

from ardtg.server.endpoints import (
    AttachSessionHandler,
    ContactsHandler,
    HealthHandler,
    WebhookHandler,
)
from ardtg.server.http_server import NiceHTTPServer

if TYPE_CHECKING:
    import logging
    import types

    import telebot

    from ardtg.domain.attach import Attacher
    from ardtg.domain.contacts import ContactStore
    from ardtg.domain.notifications import Notifier
    from ardtg.telegram.service import TelegramService


class BotApp:
    _bot: telebot.TeleBot
    _http_server: NiceHTTPServer
    _logger: logging.Logger
    _notifier: Notifier
    _telegram_service: TelegramService
    _use_webhook: bool

    def __init__(
        self,
        attacher: Attacher,
        contact_store: ContactStore,
        telegram_service: TelegramService,
        notifier: Notifier,
        webhook_url: str | None,
        bot: telebot.TeleBot,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger.getChild("bot_server")
        self._notifier = notifier
        self._bot = bot
        self._use_webhook = False
        self._http_server = NiceHTTPServer(logger)
        self._telegram_service = telegram_service

        # routes
        self._http_server.get("/contacts", ContactsHandler(contact_store, logger))
        self._http_server.get("/health", HealthHandler())
        self._http_server.post("/attach", AttachSessionHandler(attacher))
        if webhook_url is not None:
            webhook_path = f"/bot/{secrets.token_hex(16)}"
            self._http_server.post(webhook_path, WebhookHandler(bot, webhook_url + webhook_path))
            self._use_webhook = True

    def serve_http(self):
        # A serving failure is fatal, so log it and re-raise.
        try:
            self._http_server.serve_forever()
        except Exception as e:
            self._logger.error("http server is failed %s", e)
            raise e

    def run(self):
        self._telegram_service.run()

        notified: bool = False

        def notify_about_down():
            nonlocal notified
            if notified:
                return
            notified = True
            self._notifier.notify_about_down()

        ## Calls when server is take sigterm
        def _on_terminate(_signum: int, _frame: types.FrameType | None):
            self._logger.info("got SIGTERM, shutting down")
            notify_about_down()
            raise SystemExit(0)

        _ = signal.signal(signal.SIGTERM, _on_terminate)

        try:
            self._notifier.notify_about_up()

            # Run with only webhook
            if self._use_webhook:
                self._logger.info("run with webhook")
                self._http_server.serve_forever()

            # Run with infinity polling
            else:
                self._logger.info("run with polling")
                threading.Thread(target=self.serve_http, daemon=True).start()
                self._bot.infinity_polling(none_stop=True)

        finally:
            notify_about_down()
