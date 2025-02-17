import logging
from app.config import LOG_LEVEL

def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name (str): Logger name (defaults to module name)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set log level from config
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    return logger 