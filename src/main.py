import build

if __name__ == "__main__":
    build.configure_logging()

    try:
        config = build.Config()
    except Exception as e:
        raise SystemExit(f"Bad config: {e}") from e

    app = build.bot_server(config)

    app.run()
