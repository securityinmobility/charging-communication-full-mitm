import os
import logging
from datetime import datetime

def setup_logging(level=logging.INFO, log_file=None):
    """Configure logging for the entire application."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    main_log = os.path.join(log_dir, log_file if log_file else f"mitm_{timestamp}.log")
    com_log = os.path.join(log_dir, f"com_{log_file}" if log_file else f"communication_{timestamp}.log")


    # Configure Root Logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(main_log),
            logging.StreamHandler()
        ]
    )
    
    # Configure a dedicated communication Logger
    com_logger = logging.getLogger('communication')
    com_logger.setLevel(logging.INFO)
    com_handler = logging.FileHandler(com_log)
    com_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
    com_logger.addHandler(com_handler)
    com_logger.propagate = False
