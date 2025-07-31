#!/usr/bin/env python3
"""
Test Code Review
===============

A test file to demonstrate the code reviewer capabilities.
This file intentionally contains various issues for testing.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import subprocess
import tempfile

# TODO: This is a test TODO comment
# FIXME: This is a test FIXME comment

# Hardcoded secrets (for testing)
password = "secret123"
api_key = "sk-1234567890abcdef"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Long line that exceeds PEP 8 maximum length of 79 characters and should trigger a style warning
very_long_line = "This is a very long line that exceeds the recommended maximum length for Python code according to PEP 8 style guidelines"

# Bare except clause (security issue)
try:
    result = eval("2 + 2")  # Dangerous eval usage
    exec("print('Hello')")  # Dangerous exec usage
except:
    print("Caught all exceptions")

# Wildcard import (performance issue)
from os import *

# Magic numbers
def calculate_something():
    return 10000 * 2.5 + 1500

# Long function that could be refactored
def very_long_function_with_many_lines_and_complex_logic_that_should_probably_be_broken_down_into_smaller_more_focused_functions():
    """
    This is a very long function that demonstrates the need for refactoring.
    It has many lines and complex logic that should probably be broken down
    into smaller, more focused functions for better readability and maintainability.
    """
    # Some complex logic here
    data = []
    for i in range(1000):
        if i % 2 == 0:
            data.append(i * 2)
        else:
            data.append(i * 3)
    
    # More complex logic
    result = 0
    for item in data:
        if item > 100:
            result += item
        elif item > 50:
            result += item / 2
        else:
            result += item / 4
    
    # Even more logic
    processed_data = []
    for item in data:
        if item > 200:
            processed_data.append(item * 1.5)
        elif item > 100:
            processed_data.append(item * 1.2)
        else:
            processed_data.append(item)
    
    # Final calculations
    final_result = sum(processed_data) / len(processed_data) if processed_data else 0
    
    return final_result

# Class with multiple responsibilities (architecture issue)
class DataProcessor:
    """
    This class has multiple responsibilities and should be refactored.
    It handles data processing, file I/O, and network communication.
    """
    
    def __init__(self):
        self.data = []
        self.config = {}
        self.connection = None
    
    def load_data(self, filename):
        """Load data from file."""
        with open(filename, 'r') as f:
            self.data = json.load(f)
    
    def process_data(self):
        """Process the loaded data."""
        processed = []
        for item in self.data:
            if isinstance(item, dict):
                processed.append(self._transform_item(item))
        return processed
    
    def _transform_item(self, item):
        """Transform a single item."""
        return {
            'id': item.get('id', 0),
            'name': item.get('name', ''),
            'value': item.get('value', 0) * 1.1
        }
    
    def save_data(self, filename):
        """Save processed data to file."""
        with open(filename, 'w') as f:
            json.dump(self.data, f)
    
    def connect_to_database(self, host, port, username, password):
        """Connect to database."""
        # This should be in a separate DatabaseManager class
        self.connection = f"mysql://{username}:{password}@{host}:{port}"
    
    def execute_query(self, query):
        """Execute database query."""
        # This should also be in a separate DatabaseManager class
        if self.connection:
            return f"Executing: {query}"
        return None

# Inefficient string concatenation
def build_long_string():
    result = ""
    for i in range(100):
        result += f"Item {i}, "  # Inefficient string concatenation
    return result

# Console.log equivalent for testing
print("Debug: This should be removed in production")

# Main function
if __name__ == "__main__":
    # Test the code reviewer
    processor = DataProcessor()
    result = very_long_function_with_many_lines_and_complex_logic_that_should_probably_be_broken_down_into_smaller_more_focused_functions()
    print(f"Result: {result}")
    
    # Test string concatenation
    long_string = build_long_string()
    print(f"String length: {len(long_string)}") 