import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level: str = "INFO"):
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
