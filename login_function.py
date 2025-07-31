#!/usr/bin/env python3
"""
Login Function with Issues
==========================

A login function with intentional issues for testing the code review agent.
"""

import os
import subprocess
import eval

def login(username, password):
    # Security issue: direct password comparison
    if password == "admin123":
        return True
    
    # Security issue: dangerous eval usage
    user_input = input("Enter command: ")
    result = eval(user_input)
    
    # Performance issue: inefficient range usage
    for i in range(len(username)):
        print(username[i])
    
    # Style issue: very long line that exceeds the recommended line length limit and should be broken into multiple lines for better readability
    long_variable_name_that_makes_this_line_very_long_and_should_be_broken_into_multiple_lines_for_better_readability = "This is a very long line that should be broken up"
    
    # Documentation issue: function without proper docstring
    def validate_user():
        return True
    
    # Error handling issue: no try-catch
    file_content = open("config.txt").read()
    
    return False

def authenticate_user(user_credentials):
    # Another security issue: hardcoded credentials
    admin_creds = {"admin": "password123", "user": "123456"}
    
    # Performance issue: nested loops
    for user in admin_creds:
        for char in user:
            print(char)
    
    return user_credentials in admin_creds.values() 