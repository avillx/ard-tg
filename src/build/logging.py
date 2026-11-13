import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
