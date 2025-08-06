#!/usr/bin/env python3
"""
Test file for AI code review demonstration.
This file contains intentionally problematic code to test the review system.
"""

import os
import sys
import json
from typing import List, Dict, Any

# Global variable - bad practice
global_data = {}

def process_user_data(user_input: str) -> Dict[str, Any]:
    """
    Process user data without proper validation.
    This function has several security and best practice issues.
    """
    # No input validation
    result = eval(user_input)  # SECURITY ISSUE: eval() is dangerous
    
    # Hardcoded credentials - bad practice
    api_key = "sk-1234567890abcdef"
    password = "admin123"
    
    # No error handling
    data = json.loads(user_input)
    
    # Inefficient loop
    items = []
    for i in range(1000):
        items.append(i)
    
    # Unused variable
    unused_var = "this is never used"
    
    # Magic numbers
    if len(data) > 100:
        return {"status": "too large"}
    
    # No type hints for return
    return result

def calculate_total(numbers: List[int]) -> int:
    """
    Calculate total with inefficient implementation.
    """
    total = 0
    for num in numbers:
        total = total + num  # Could use +=
    
    # No validation for empty list
    return total

def fetch_data(url: str) -> str:
    """
    Fetch data without proper error handling.
    """
    import requests
    
    # No timeout specified
    response = requests.get(url)
    
    # No status code checking
    return response.text

def main():
    """
    Main function with poor structure.
    """
    # No proper argument parsing
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = "print('hello')"
    
    # Call dangerous function
    result = process_user_data(user_input)
    
    # Print sensitive data
    print(f"API Key: {api_key}")
    print(f"Result: {result}")

if __name__ == "__main__":
    main() 