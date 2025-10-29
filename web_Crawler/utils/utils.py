import logging
import yaml
import os 
import datetime
from datetime import datetime
def prepare_log(name, log_dir):
    """Prepare a logger that logs to both file and console."""
    os.makedirs(log_dir, exist_ok=True)

    # Log filename by date
    log_file = os.path.join(log_dir, f"{datetime.now():%Y-%m-%d}.log")

    # Configure format
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(console_handler)

    return logger
def load_config(config_path):
    """Load YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config
def prepare_folder(root_dir,purpose):
    """Prepare folder for serving specific purpose."""
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    folder_path =  os.path.join(root_dir,purpose)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
