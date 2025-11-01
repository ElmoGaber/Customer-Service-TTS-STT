import logging

def setup_logger(log_path: str):
    """Setup logger configuration"""
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("whisper_logger")
