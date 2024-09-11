import logging

import colorlog

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        handler,
    ],
)

logger = logging.getLogger(__name__)
