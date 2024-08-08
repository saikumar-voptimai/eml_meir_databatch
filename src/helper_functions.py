from box import Box
from pathlib import Path
import logging.config
import logging.handlers
import yaml
from typing import List

root_path = Path(__file__).resolve().parents[1]

def load_config() -> Box:
    """
    Load the configuration from a YAML file.
    :return: Box object containing the configuration data
    """
    with open(root_path / "src" / "config" / "config.yml", "r") as file:
        config = yaml.safe_load(file)
    return Box(config)

def load_variables() -> List[str]:
    """
    Load variables from a text file.
    :return: List of variables
    """
    with open(root_path / "data" / "variables_load.txt", "r") as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def setup_logging() -> None:
    """
    Setup logging configuration.
    :return: None
    """
    logger_config_file = root_path / "logs" / "config_logger.yml"
    with open(logger_config_file) as f_in:
        config = yaml.safe_load(f_in)
    logging.config.dictConfig(config)
