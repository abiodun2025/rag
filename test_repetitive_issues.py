#!/usr/bin/env python3
"""
Test file with repetitive code patterns to test deduplication
"""

# Multiple hardcoded secrets (should be grouped)
password = "secret123"
api_key = "sk-1234567890abcdef"
private_key = "-----BEGIN PRIVATE KEY-----"
token = "ghp_abcdef123456"

# Multiple file operations without error handling (should be grouped)
file1 = open("data1.txt", "r")
content1 = file1.read()
file1.close()

file2 = open("data2.txt", "w")
file2.write("some data")
file2.close()

file3 = open("data3.txt", "r")
content3 = file3.read()
file3.close()

# Multiple network requests without error handling (should be grouped)
import requests
response1 = requests.get("https://api.example.com/data1")
response2 = requests.get("https://api.example.com/data2")
response3 = requests.post("https://api.example.com/upload")

# Multiple TODO comments (should be grouped)
# TODO: Implement error handling
# TODO: Add logging
# TODO: Fix this later

# Multiple magic numbers (should be grouped)
timeout = 5000
max_retries = 3
buffer_size = 1024
port = 8080

# Multiple nested conditionals (should be grouped)
if user.is_admin:
    if user.has_permission:
        if user.is_active:
            if user.can_write:
                do_something()

if user.is_moderator:
    if user.has_permission:
        if user.is_active:
            if user.can_read:
                do_something_else()

# Multiple long method chains (should be grouped)
result = user.get_profile().get_settings().get_preferences().get_theme().get_colors().get_primary()
data = api.get_data().filter_by_type("user").sort_by_date().limit(10).get_results() 