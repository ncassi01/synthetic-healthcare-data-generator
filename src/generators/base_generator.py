"""
Base generator for the synthetic healthcare data generator.

This module defines the base class for all data generators.
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


class BaseGenerator(ABC):
    """Base class for all data generators."""
    
    def __init__(self, config: Dict[str, Any], seed: Optional[int] = None):
        """
        Initialize the base generator.
        
        Args:
            config: Configuration dictionary for the generator.
            seed: Random seed for reproducibility.
        """
        self.config = config
        self.seed = seed
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set random seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
    
    @abstractmethod
    def generate(self, count: int) -> List[Any]:
        """
        Generate synthetic data.
        
        Args:
            count: Number of items to generate.
            
        Returns:
            List of generated items.
        """
        pass
    
    def save_to_json(self, data: List[Any], output_path: str) -> None:
        """
        Save generated data to a JSON file.
        
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
        
        self.logger.info(f"Saved {len(data)} items to {output_path}")