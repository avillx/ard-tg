import sys

import build

if __name__ == "__main__":
    build.configure_logging()

    try:
        config = build.Config()
    except Exception as e:
        print(f"Bad config: {e}")
        sys.exit(1)

    app = build.bot_server(config)

    app.run()
