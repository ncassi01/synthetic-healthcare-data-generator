"""
Base processor for the synthetic healthcare data generator.

This module defines the base class for all data processors.
"""

import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Add the parent directory to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np


class BaseProcessor(ABC):
    """Base class for all data processors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base processor.
        
        Args:
            config: Configuration dictionary for the processor.
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def process(self, data: List[Any]) -> List[Any]:
        """
        Process the input data.
        
        Args:
            data: List of data items to process.
            
        Returns:
            List of processed data items.
        """
        pass
    
    def save_to_json(self, data: List[Any], output_path: str) -> None:
        """
        Save processed data to a JSON file.
        
        Args:
            data: List of data items to save.
            output_path: Path to save the JSON file.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert data to JSON-serializable format if needed
        serializable_data = []
        for item in data:
            if hasattr(item, 'to_dict'):
                serializable_data.append(item.to_dict())
            else:
                serializable_data.append(item)
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        self.logger.info(f"Saved {len(data)} processed items to {output_path}")