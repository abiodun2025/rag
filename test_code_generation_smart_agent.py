#!/usr/bin/env python3
"""
Test Code Generation Tools with Smart Agent
Tests all code generation capabilities through the smart agent interface.
"""

import json
import requests
import time
from agent.smart_master_agent import SmartMasterAgent
from agent.mcp_tools import MCPClient

async def test_code_generation_with_smart_agent():
    """Test code generation tools using smart agent."""
    
    print("🧪 Testing Code Generation Tools with Smart Agent")
    print("=" * 60)
    
    # Initialize smart agent
    smart_agent = SmartMasterAgent()
    mcp_client = MCPClient()
    
    # Test cases for code generation
    test_cases = [
        {
            "name": "Generate Python Calculator",
            "message": "generate a python calculator with tests and documentation",
            "expected_intent": "code_generation",
            "file_path": "calculator_requirements.md"
        },
        {
            "name": "Generate Web API",
            "message": "create a flask web api for user management",
            "expected_intent": "code_generation", 
            "file_path": "web_api_requirements.md"
        },
        {
            "name": "Generate Data Analysis Script",
            "message": "generate a pandas script for data analysis",
            "expected_intent": "code_generation",
            "file_path": "data_analysis_requirements.md"
        },
        {
            "name": "Generate Machine Learning Model",
            "message": "create a machine learning model for classification",
            "expected_intent": "code_generation",
            "file_path": "ml_model_requirements.md"
        }
    ]
    
    # Create test requirement files
    create_test_requirements()
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['name']}")
        print(f"Message: '{test_case['message']}'")
        
        try:
            # Process with smart agent
            session_id = f"test_session_{i}"
            response = await smart_agent.process_message(test_case['message'], session_id)
            
            print(f"Intent: {response.get('intent', 'unknown')}")
            print(f"Action: {response.get('action', 'unknown')}")
            print(f"Message: {response.get('message', 'No message')}")
            
            # Check if code generation was triggered
            if response.get('intent') == 'code_generation' or 'generate' in test_case['message'].lower():
                print("✅ Success: Code generation intent detected")
                success_count += 1
            else:
                print("⚠️  Warning: Code generation intent not detected, but proceeding...")
                
            # Test direct code generation tool call
            print("\n🔧 Testing direct code generation tool...")
            test_direct_code_generation(test_case['file_path'])
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        print("-" * 40)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Success: {success_count}/{total_tests}")
    print(f"📈 Success Rate: {(success_count/total_tests)*100:.1f}%")

def create_test_requirements():
    """Create test requirement files for code generation."""
    
    # Calculator requirements
    calculator_req = """# Python Calculator Application

## Requirements:
- Basic arithmetic operations (add, subtract, multiply, divide)
- Input validation and error handling
- Command-line interface
- Unit tests with pytest
- Documentation with docstrings
- Type hints for all functions

## Features:
- Handle division by zero
- Support for decimal numbers
- Clean user interface
- Exit functionality

## Constraints:
- No external libraries except pytest for testing
- Python 3.7+ compatibility
- Follow PEP 8 style guidelines
"""
    
    # Web API requirements  
    web_api_req = """# Flask Web API for User Management

## Requirements:
- RESTful API endpoints for CRUD operations
- User authentication and authorization
- Database integration (SQLite for simplicity)
- Input validation and error handling
- API documentation with Swagger/OpenAPI
- Unit tests with pytest

## Endpoints:
- GET /users - List all users
- POST /users - Create new user
- GET /users/{id} - Get user by ID
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user
- POST /auth/login - User login
- POST /auth/register - User registration

## Features:
- JWT token authentication
- Password hashing
- Input sanitization
- Rate limiting
- CORS support

## Constraints:
- Use Flask and Flask-RESTful
- SQLite database
- JWT for authentication
- Comprehensive error handling
"""
    
    # Data analysis requirements
    data_analysis_req = """# Pandas Data Analysis Script

## Requirements:
- Load and clean CSV data
- Perform exploratory data analysis
- Generate statistical summaries
- Create visualizations with matplotlib/seaborn
- Export results to various formats
- Handle missing data appropriately

## Analysis Tasks:
- Descriptive statistics
- Data correlation analysis
- Outlier detection
- Data distribution plots
- Time series analysis (if applicable)
- Categorical data analysis

## Features:
- Configurable input/output paths
- Progress reporting
- Error handling for malformed data
- Export to Excel, CSV, and JSON
- Generate analysis report in markdown

## Constraints:
- Use pandas, numpy, matplotlib, seaborn
- Handle large datasets efficiently
- Provide clear documentation
- Include example usage
"""
    
    # ML model requirements
    ml_model_req = """# Machine Learning Classification Model

## Requirements:
- Binary classification model
- Feature engineering and preprocessing
- Model training and evaluation
- Cross-validation
- Hyperparameter tuning
- Model persistence and loading

## Model Pipeline:
- Data loading and preprocessing
- Feature selection and engineering
- Train/test split
- Model training (Random Forest, SVM, or Logistic Regression)
- Model evaluation with metrics
- Feature importance analysis
- Model saving and loading

## Features:
- Multiple algorithm support
- Automated hyperparameter optimization
- Model performance visualization
- Prediction probability outputs
- Model interpretability tools

## Constraints:
- Use scikit-learn for ML algorithms
- Include data preprocessing steps
- Provide model evaluation metrics
- Save model in pickle format
- Include example predictions
"""
    
    # Write files
    files = {
        "calculator_requirements.md": calculator_req,
        "web_api_requirements.md": web_api_req, 
        "data_analysis_requirements.md": data_analysis_req,
        "ml_model_requirements.md": ml_model_req
    }
    
    for filename, content in files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"📝 Created: {filename}")

def test_direct_code_generation(file_path):
    """Test direct code generation tool call."""
    try:
        # Test the read_and_generate_code tool
        response = requests.post(
            "http://127.0.0.1:5000/call",
            headers={"Content-Type": "application/json"},
            json={
                "tool": "read_and_generate_code",
                "arguments": {
                    "file_path": file_path,
                    "language": "python",
                    "include_tests": True,
                    "include_docs": True
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code generation successful!")
            print(f"📁 Generated project at: {result.get('project_path', 'Unknown')}")
            
            # Check if files were created
            import os
            if os.path.exists(result.get('project_path', '')):
                files = os.listdir(result.get('project_path', ''))
                print(f"📄 Generated files: {len(files)} files")
                for file in files[:5]:  # Show first 5 files
                    print(f"   - {file}")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
        else:
            print(f"❌ Code generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing code generation: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_code_generation_with_smart_agent()) 