#!/usr/bin/env python3
"""
Test script for GitHub AI Code Review Agent
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_environment_setup():
    """Test that all required environment variables are set."""
    logger.info("🔧 Testing environment setup...")
    
    required_vars = [
        "GITHUB_APP_ID",
        "GITHUB_PRIVATE_KEY", 
        "GITHUB_WEBHOOK_SECRET",
        "COHERE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        logger.error("Please set these variables in your .env file")
        return False
    
    logger.info("✅ All environment variables are set")
    return True


def test_github_client():
    """Test GitHub client initialization."""
    logger.info("🔧 Testing GitHub client...")
    
    try:
        from app.github_client import GitHubClient
        from app.config import settings
        
        client = GitHubClient()
        
        # Test JWT generation
        jwt_token = client._generate_jwt()
        if jwt_token:
            logger.info("✅ JWT token generation successful")
        else:
            logger.error("❌ JWT token generation failed")
            return False
        
        logger.info("✅ GitHub client initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ GitHub client test failed: {e}")
        return False


def test_code_review_service():
    """Test code review service initialization."""
    logger.info("🔧 Testing code review service...")
    
    try:
        from app.code_review_service import CodeReviewService
        
        service = CodeReviewService()
        
        # Test Cohere client initialization
        if hasattr(service, 'cohere_client'):
            logger.info("✅ Cohere client initialization successful")
        else:
            logger.error("❌ Cohere client initialization failed")
            return False
        
        logger.info("✅ Code review service initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Code review service test failed: {e}")
        return False


async def test_manual_code_review():
    """Test manual code review functionality."""
    logger.info("🔧 Testing manual code review...")
    
    try:
        from app.code_review_service import CodeReviewService
        
        service = CodeReviewService()
        
        # Sample code diff for testing
        sample_diff = """
diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 def hello_world():
-    print("Hello, World!")
+    # Add a comment
+    print("Hello, World!")  # This is a greeting
+    return True
"""
        
        # Test manual review
        result = await service.review_code(
            diff_content=sample_diff,
            changed_files=["test.py"]
        )
        
        if result["success"]:
            logger.info(f"✅ Manual code review successful")
            logger.info(f"   Generated {len(result.get('comments', []))} comments")
            logger.info(f"   Summary: {result.get('summary', 'No summary')}")
            return True
        else:
            logger.error(f"❌ Manual code review failed: {result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Manual code review test failed: {e}")
        return False


def test_webhook_signature_verification():
    """Test webhook signature verification."""
    logger.info("🔧 Testing webhook signature verification...")
    
    try:
        from app.github_client import GitHubClient
        
        client = GitHubClient()
        
        # Test with sample payload and signature
        sample_payload = b'{"test": "data"}'
        sample_signature = "sha256=invalid_signature"
        
        # This should return False for invalid signature
        result = client.verify_webhook_signature(sample_payload, sample_signature)
        
        if not result:
            logger.info("✅ Webhook signature verification working (correctly rejected invalid signature)")
            return True
        else:
            logger.error("❌ Webhook signature verification failed (accepted invalid signature)")
            return False
        
    except Exception as e:
        logger.error(f"❌ Webhook signature verification test failed: {e}")
        return False


def test_fastapi_app():
    """Test FastAPI app initialization."""
    logger.info("🔧 Testing FastAPI app...")
    
    try:
        from app.main import app
        
        # Test that app is created
        if app:
            logger.info("✅ FastAPI app initialization successful")
            
            # Test that endpoints are registered
            routes = [route.path for route in app.routes]
            expected_routes = ["/", "/health", "/webhook/github", "/review"]
            
            for route in expected_routes:
                if route in routes:
                    logger.info(f"✅ Route {route} registered")
                else:
                    logger.warning(f"⚠️  Route {route} not found")
            
            return True
        else:
            logger.error("❌ FastAPI app initialization failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ FastAPI app test failed: {e}")
        return False


def create_sample_webhook_payload():
    """Create a sample webhook payload for testing."""
    return {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "title": "Test PR",
            "body": "This is a test pull request",
            "user": {"login": "testuser"},
            "head": {"ref": "feature/test"},
            "base": {"ref": "main"}
        },
        "repository": {
            "name": "test-repo",
            "owner": {"login": "testowner"},
            "full_name": "testowner/test-repo"
        },
        "sender": {"login": "testuser"},
        "installation": {"id": 12345}
    }


async def run_all_tests():
    """Run all tests."""
    logger.info("🚀 Starting GitHub AI Code Review Agent tests...")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("GitHub Client", test_github_client),
        ("Code Review Service", test_code_review_service),
        ("Webhook Signature Verification", test_webhook_signature_verification),
        ("FastAPI App", test_fastapi_app),
        ("Manual Code Review", test_manual_code_review),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The code review agent is ready to use.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Please fix the issues before using the agent.")
        return False


def print_setup_instructions():
    """Print setup instructions."""
    logger.info(f"\n{'='*50}")
    logger.info("SETUP INSTRUCTIONS")
    logger.info(f"{'='*50}")
    
    logger.info("""
To run the GitHub AI Code Review Agent:

1. Set up environment variables in .env file:
   GITHUB_APP_ID=your_app_id
   GITHUB_PRIVATE_KEY=your_private_key_or_path
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   COHERE_API_KEY=your_cohere_api_key

2. Install dependencies:
   pip install fastapi uvicorn cohere PyGithub python-jose[cryptography] python-dotenv

3. Run the server:
   python -m app.main

4. Configure GitHub webhook:
   - URL: http://your-domain/webhook/github
   - Content type: application/json
   - Events: Pull requests

5. Test the agent:
   python test_code_review_agent.py
""")


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    
    if not success:
        print_setup_instructions() 