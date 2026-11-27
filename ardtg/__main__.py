from ardtg.build.config import ConfigError, Config
from ardtg.build.di import build_app
from ardtg.build.logging import configure_logging

if __name__ == "__main__":
    configure_logging()

    try:
        config = Config()
    except ConfigError as err:
        raise SystemExit(f"Bad config: {err}") from err

    app = build_app(config)
    app.run()
