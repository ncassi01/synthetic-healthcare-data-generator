"""
File utility functions for the synthetic healthcare data generator.

This module provides utility functions for file operations.
"""

import json
import logging
import os
from typing import Any, Dict


logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Configuration dictionary.
        
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    logger.info(f"Loading configuration from {config_path}")
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Successfully loaded configuration from {config_path}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def ensure_directory(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory.
    """
    if not os.path.exists(directory_path):
        logger.info(f"Creating directory: {directory_path}")
        os.makedirs(directory_path, exist_ok=True)
    else:
        logger.debug(f"Directory already exists: {directory_path}")


def get_output_path(base_dir: str, filename: str) -> str:
    """
    Get the full path for an output file.
    
    Args:
        base_dir: Base directory for output files.
        filename: Name of the output file.
        
    Returns:
        Full path to the output file.
    """
    ensure_directory(base_dir)
    return os.path.join(base_dir, filename)