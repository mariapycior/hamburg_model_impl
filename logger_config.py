import logging
import os
from datetime import datetime

def setup_logger(name):
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')
    
    # Create file handler (debug level - wszystkie logi)
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'simulation_{current_time}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler (info level - tylko końcowe komunikaty)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)
    
    # Setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
