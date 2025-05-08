import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name="league_bot", log_level=logging.INFO):
    """Configure and return a logger instance"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating logs)
    file_handler = RotatingFileHandler(
        f"logs/{datetime.now().strftime('%Y%m%d')}_{name}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Example usage:
logger = setup_logger()
logger.info("Application started")
logger.warning("Low health detected!")
logger.error("Failed to click at position")