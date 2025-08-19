#!/usr/bin/env python3
"""
Test file demonstrating 100+ unique comment types the agent can detect.
This file intentionally contains various code quality issues for testing purposes.
"""

# Security issues
password = "admin123"  # Critical: hardcoded admin password
api_key = "sk-1234567890abcdef"  # Critical: AI service API key exposed
private_key = "-----BEGIN RSA PRIVATE KEY-----"  # Critical: cryptographic private key
token = "ghp_abcdef123456"  # Critical: GitHub PAT hardcoded
secret = "super_secret_value"  # Critical: hardcoded secret

# SQL injection patterns
query = f"SELECT * FROM users WHERE id = {user_id}"  # Critical: SQL injection
sql = "INSERT INTO logs VALUES (" + log_data + ")"  # Critical: SQL injection

# Weak cryptography
import hashlib
hash_value = hashlib.md5(password.encode()).hexdigest()  # High: MD5 usage
hash_value2 = hashlib.sha1(password.encode()).hexdigest()  # High: SHA-1 usage

# Command injection
import os
os.system(f"rm -rf {user_input}")  # Critical: command injection
import subprocess
subprocess.call(["rm", "-rf", user_input])  # High: shell command execution

# XSS vulnerabilities
element.innerHTML = user_input  # Critical: XSS vulnerability
document.write(user_data)  # Critical: XSS vulnerability

# Insecure protocols
url = "http://external-api.com/data"  # High: insecure HTTP protocol

# Authentication bypass
admin = True  # Critical: hardcoded admin access
role = "admin"  # Critical: hardcoded admin access
is_admin = 1  # Critical: hardcoded admin access

# Session management
session_timeout = 0  # High: infinite session lifetime
remember_me = True  # Medium: remember me without security

# File upload security
# enctype="multipart/form-data"  # High: file upload without validation

# Deserialization security
import pickle
data = pickle.loads(user_input)  # Critical: unsafe pickle deserialization
import yaml
config = yaml.load(file_content)  # High: unsafe YAML deserialization

# Error handling issues
file = open("data.txt", "r")  # High: file operation without error handling
content = file.read()  # High: file read without error handling
file.close()

# Network operations without error handling
import requests
response = requests.get("https://api.example.com/data")  # High: HTTP request without error handling
data = response.json()  # High: JSON parsing without error handling

# Database operations without error handling
cursor.execute("SELECT * FROM users")  # High: database operation without error handling
result = cursor.fetchall()  # High: database operation without error handling

# JSON parsing without error handling
import json
data = json.loads(user_input)  # Medium: JSON parsing without error handling

# Network timeout issues
requests.get("https://api.example.com", timeout=0)  # High: infinite timeout
requests.get("https://api.example.com", retry=0)  # Medium: retry disabled

# Exception handling
try:
    risky_operation()
except:  # High: bare except clause
    pass

try:
    risky_operation()
except Exception:  # Medium: generic exception handling
    pass

# Logging issues
print("Debug info")  # Medium: print statement in production
console.log("Debug info")  # Medium: console.log in production

# Performance issues
setInterval(updateUI, 100)  # Medium: setInterval without cleanup
setTimeout(processData, 1000)  # Medium: setTimeout without cleanup

# Memory management
addEventListener("click", handleClick)  # Medium: event listener without cleanup
new File("data.txt")  # Medium: resource creation without cleanup

# Concurrency issues
import threading
thread = threading.Thread(target=worker)  # High: thread without synchronization
thread.start()

# Input validation
user_input = input("Enter data: ")  # Medium: user input without validation
command_line_arg = sys.argv[1]  # Medium: command line input without validation

# Web input validation
request_data = request.json  # High: JSON request without validation
form_data = request.form  # High: form data without validation

# Framework-specific issues
from django.db import models
class User(models.Model):
    name = models.CharField()  # Medium: CharField without max_length
    created = models.DateTimeField()  # Low: DateTimeField without auto timestamps

# Database patterns
cursor.execute("SELECT * FROM users")  # Medium: SELECT * query
cursor.execute("SELECT COUNT(*) FROM large_table")  # Low: COUNT(*) for large table

# API design
@app.route("/api/v1/users")  # Low: API versioning in URL path
def get_users():
    return jsonify(users)  # Medium: endpoint without authentication

# Configuration issues
config.host = "localhost"  # Medium: hardcoded configuration
config.env = "dev"  # Low: development-only configuration

# Code quality
magic_number = 86400  # Medium: magic number in timing
buffer_size = 1024  # Medium: magic number in size
port = 8080  # Medium: hardcoded port
version = "1.0.0"  # Medium: hardcoded version

# String concatenation
sql_query = "SELECT * FROM " + table_name + " WHERE id = " + user_id  # High: SQL with concatenation
url = "https://api.com/" + endpoint + "?key=" + api_key  # Medium: URL with concatenation

# Variable naming
a = 1  # Low: variable name too short
data = []  # Medium: generic variable name
stuff = {}  # Medium: generic variable name

# Function complexity
complex_function_call(if condition1 and condition2 and condition3)  # Medium: complex function call

# Loop patterns
for i in range(len(items)):  # Low: index-based loop with len()

# Nested conditionals
if user.is_authenticated and user.has_permission and user.is_active and user.role == "admin":  # Medium: complex authorization
    pass

# Long method chains
result = api_client.get_data().filter_by_status("active").sort_by_date().limit(10).execute()  # Medium: long method chain

# Hardcoded paths
log_file = "/usr/local/logs/app.log"  # Medium: hardcoded log path
data_dir = "/home/user/data"  # Medium: hardcoded user path
temp_file = "/tmp/temp.txt"  # Medium: hardcoded temp path

# TODO comments with context
# TODO: implement error handling  # Medium: TODO for error handling
# FIXME: add unit tests  # Medium: TODO for testing
# NOTE: add logging here  # Low: TODO for logging
# XXX: validate user input  # Medium: TODO for validation
# BUG: optimize performance  # Medium: TODO for performance

# Language-specific issues
from module import *  # Medium: wildcard import
lambda_func = lambda x: x * 2 if x > 0 else x * 3 if x < 0 else 0  # Low: complex lambda

# Cloud and deployment
aws_access_key = "AKIA1234567890"  # Critical: AWS credentials hardcoded
aws_region = "us-east-1"  # Low: hardcoded AWS region

# Docker issues
# FROM ubuntu:latest  # Medium: latest tag in Docker
# RUN apt-get update && apt-get install -y package  # Medium: Docker layer optimization

# Monitoring and observability
log.info("User action")  # Low: logging without level specification
metrics.record("operation")  # Low: generic metrics collection

# Accessibility and internationalization
# <img src="image.jpg" alt="">  # Medium: empty alt attribute
# <html lang="en">  # Low: hardcoded language attribute

# Modern development practices
var oldVariable = "value"  # Low: var keyword usage
function oldFunction() {}  # Low: function declaration syntax

# Testing patterns
def test_user_creation():
    # Test without assertions
    user = create_user("test")
    # Low: test function without assertions

# Documentation
def undocumented_function():
    # No docstring
    pass  # Low: function without docstring

class UndocumentedClass:
    # No docstring
    pass  # Low: class without docstring 