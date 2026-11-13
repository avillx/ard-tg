import secrets
import signal
import threading
lazy import logging
lazy import types

lazy import telebot

from server import endpoints, http_server
lazy import attach
lazy import contacts
lazy import notifications


class BotServer:
    _bot: telebot.TeleBot
    _http_server: http_server.Server
    _logger: logging.Logger
    _notifier: notifications.Notifier
    _use_webhook: bool

    def __init__(
        self,
        attachment_service: attach.AttachService,
        contact_service: contacts.ContactService,
        notifier: notifications.Notifier,
        webhook_url: str,
        bot: telebot.TeleBot,
        logger: logging.Logger,
    ) -> None:
        self._logger = logger.getChild("bot_server")
        self._notifier = notifier
        self._bot = bot
        self._use_webhook = False
        self._http_server = http_server.Server(logger)

        # routes
        self._http_server.post("/attach", endpoints.AttachSessionHandler(attachment_service))
        if webhook_url != "":
            webhook_path = f"/bot/{secrets.token_hex(16)}"
            self._http_server.post(
                webhook_path, endpoints.WebhookHandler(bot, webhook_url + webhook_path)
            )
            self._use_webhook = True

        self._http_server.get("/contacts", endpoints.ContactsHandler(contact_service))
        self._http_server.get("/health", endpoints.HealthHandler())

    def serve_http(self):
        # A serving failure is fatal, so log it and re-raise.
        try:
            self._http_server.serve_forever()
        except Exception as e:
            self._logger.error("http server is failed %s", e)
            raise e

    def run(self):

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
