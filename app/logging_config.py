import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        rename_fields={"asctime": "timestamp", "levelname": "level"}
    )
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid double logging
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(log_handler)
    
    # Also configure Flask's logger specifically
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
