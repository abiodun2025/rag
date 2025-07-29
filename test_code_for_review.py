#!/usr/bin/env python3
"""
Test file for automated code review
This file contains various code patterns to test the review agent.
"""

import os
import requests

def insecure_function(user_input):
    """This function has security issues."""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    # This is vulnerable to SQL injection
    return execute_query(query)

def performance_issue():
    """This function has performance issues."""
    users = get_all_users()
    for user in users:
        # N+1 query problem
        profile = get_user_profile(user.id)
        print(profile.name)

def style_issues():
    """This function has style issues."""
    x = 42  # Magic number
    if x > 40:
        print("Value is high")
    
    # Long function with many lines
    for i in range(100):
        print(f"Line {i}")
        if i % 10 == 0:
            print("Multiple of 10")
        elif i % 5 == 0:
            print("Multiple of 5")
        else:
            print("Regular number")

def good_function():
    """This function follows good practices."""
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    try:
        response = requests.get("https://api.example.com/data", timeout=TIMEOUT)
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    insecure_function("admin")
    performance_issue()
    style_issues()
    good_function()
