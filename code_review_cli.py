#!/usr/bin/env python3
"""
GitHub AI Code Review Agent CLI
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeReviewCLI:
    """CLI for GitHub AI Code Review Agent."""
    
    def __init__(self):
        self.test_diff = """
diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,10 +1,15 @@
 def calculate_total(items):
-    total = 0
-    for item in items:
-        total += item
-    return total
+    # Calculate total with validation
+    if not items:
+        return 0
+    
+    total = sum(items)  # More efficient than loop
+    
+    # Add logging for debugging
+    print(f"Total calculated: {total}")
+    return total

 def process_data(data):
-    result = data * 2
-    return result
+    # Add input validation
+    if data is None:
+        return None
+    
+    result = data * 2
+    return result
"""

    async def test_environment(self):
        """Test environment configuration."""
        logger.info("🔧 Testing environment configuration...")
        
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
            return False
        
        logger.info("✅ All environment variables are set")
        return True

    async def test_github_client(self):
        """Test GitHub client."""
        logger.info("🔧 Testing GitHub client...")
        
        try:
            from app.github_client import GitHubClient
            
            client = GitHubClient()
            jwt_token = client._generate_jwt()
            
            if jwt_token:
                logger.info("✅ GitHub client test passed")
                return True
            else:
                logger.error("❌ GitHub client test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ GitHub client test failed: {e}")
            return False

    async def test_code_review_service(self):
        """Test code review service."""
        logger.info("🔧 Testing code review service...")
        
        try:
            from app.code_review_service import CodeReviewService
            
            service = CodeReviewService()
            
            # Test manual review
            result = await service.review_code(
                diff_content=self.test_diff,
                changed_files=["example.py"]
            )
            
            if result["success"]:
                logger.info(f"✅ Code review service test passed")
                logger.info(f"   Generated {len(result.get('comments', []))} comments")
                logger.info(f"   Summary: {result.get('summary', 'No summary')}")
                return True
            else:
                logger.error(f"❌ Code review service test failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Code review service test failed: {e}")
            return False

    async def test_webhook_signature(self):
        """Test webhook signature verification."""
        logger.info("🔧 Testing webhook signature verification...")
        
        try:
            from app.github_client import GitHubClient
            
            client = GitHubClient()
            
            # Test with invalid signature
            sample_payload = b'{"test": "data"}'
            sample_signature = "sha256=invalid_signature"
            
            result = client.verify_webhook_signature(sample_payload, sample_signature)
            
            if not result:
                logger.info("✅ Webhook signature verification test passed")
                return True
            else:
                logger.error("❌ Webhook signature verification test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Webhook signature verification test failed: {e}")
            return False

    async def test_fastapi_app(self):
        """Test FastAPI app."""
        logger.info("🔧 Testing FastAPI app...")
        
        try:
            from app.main import app
            
            if app:
                routes = [route.path for route in app.routes]
                expected_routes = ["/", "/health", "/webhook/github", "/review"]
                
                missing_routes = [route for route in expected_routes if route not in routes]
                
                if not missing_routes:
                    logger.info("✅ FastAPI app test passed")
                    return True
                else:
                    logger.error(f"❌ Missing routes: {missing_routes}")
                    return False
            else:
                logger.error("❌ FastAPI app test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ FastAPI app test failed: {e}")
            return False

    async def run_review(self, diff_content: str, files: list):
        """Run a manual code review."""
        logger.info("🔍 Running manual code review...")
        
        try:
            from app.code_review_service import CodeReviewService
            
            service = CodeReviewService()
            
            result = await service.review_code(
                diff_content=diff_content,
                changed_files=files
            )
            
            if result["success"]:
                logger.info("✅ Code review completed")
                logger.info(f"   Comments: {len(result.get('comments', []))}")
                logger.info(f"   Summary: {result.get('summary', 'No summary')}")
                
                # Print comments
                for i, comment in enumerate(result.get('comments', []), 1):
                    logger.info(f"   Comment {i}: Line {comment.line} - {comment.body}")
                
                return True
            else:
                logger.error(f"❌ Code review failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Code review failed: {e}")
            return False

    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the FastAPI server."""
        logger.info(f"🚀 Starting server on {host}:{port}...")
        
        try:
            import uvicorn
            from app.main import app
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")

    def print_help(self):
        """Print help information."""
        help_text = """
GitHub AI Code Review Agent CLI

Commands:
  test-env          Test environment configuration
  test-github       Test GitHub client
  test-service      Test code review service
  test-webhook      Test webhook signature verification
  test-app          Test FastAPI app
  test-all          Run all tests
  review            Run manual code review
  server            Start the server
  help              Show this help

Examples:
  python code_review_cli.py test-all
  python code_review_cli.py review
  python code_review_cli.py server --host 127.0.0.1 --port 8000
"""
        print(help_text)

    async def run_tests(self):
        """Run all tests."""
        logger.info("🚀 Running all tests...")
        
        tests = [
            ("Environment", self.test_environment),
            ("GitHub Client", self.test_github_client),
            ("Code Review Service", self.test_code_review_service),
            ("Webhook Signature", self.test_webhook_signature),
            ("FastAPI App", self.test_fastapi_app),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
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


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="GitHub AI Code Review Agent CLI")
    parser.add_argument("command", choices=[
        "test-env", "test-github", "test-service", "test-webhook", 
        "test-app", "test-all", "review", "server", "help"
    ], help="Command to run")
    
    parser.add_argument("--host", default="0.0.0.0", help="Server host (for server command)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (for server command)")
    parser.add_argument("--diff", help="Diff content for review (for review command)")
    parser.add_argument("--files", nargs="+", help="Changed files for review (for review command)")
    
    args = parser.parse_args()
    
    cli = CodeReviewCLI()
    
    if args.command == "help":
        cli.print_help()
    elif args.command == "test-env":
        await cli.test_environment()
    elif args.command == "test-github":
        await cli.test_github_client()
    elif args.command == "test-service":
        await cli.test_code_review_service()
    elif args.command == "test-webhook":
        await cli.test_webhook_signature()
    elif args.command == "test-app":
        await cli.test_fastapi_app()
    elif args.command == "test-all":
        await cli.run_tests()
    elif args.command == "review":
        diff_content = args.diff or cli.test_diff
        files = args.files or ["example.py"]
        await cli.run_review(diff_content, files)
    elif args.command == "server":
        await cli.start_server(args.host, args.port)
    else:
        logger.error(f"Unknown command: {args.command}")
        cli.print_help()


if __name__ == "__main__":
    asyncio.run(main()) 