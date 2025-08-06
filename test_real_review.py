#!/usr/bin/env python3
"""
Test script to demonstrate real code review functionality.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_real_code_review():
    """Test the code review service with real problematic code."""
    
    # Read the test file
    with open('test_code_for_review.py', 'r') as f:
        code_content = f.read()
    
    # Create a diff-like content
    diff_content = f"""
diff --git a/test_code_for_review.py b/test_code_for_review.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test_code_for_review.py
@@ -0,0 +1,80 @@
+{code_content}
"""
    
    logger.info("🔍 Testing real code review with problematic code...")
    
    try:
        from app.code_review_service import CodeReviewService
        
        service = CodeReviewService()
        
        # Test the review
        result = await service.review_code(
            diff_content=diff_content,
            changed_files=["test_code_for_review.py"]
        )
        
        if result["success"]:
            logger.info("✅ Code review completed successfully!")
            logger.info(f"📝 Generated {len(result.get('comments', []))} comments")
            logger.info(f"📋 Summary: {result.get('summary', 'No summary')}")
            
            # Print detailed comments
            logger.info("\n" + "="*60)
            logger.info("DETAILED REVIEW COMMENTS")
            logger.info("="*60)
            
            for i, comment in enumerate(result.get('comments', []), 1):
                logger.info(f"\n🔍 Comment {i}:")
                logger.info(f"   Line: {comment.line}")
                logger.info(f"   Issue: {comment.body}")
                
        else:
            logger.error(f"❌ Code review failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")


async def test_github_integration():
    """Test GitHub integration with real repository."""
    
    logger.info("🔗 Testing GitHub integration...")
    
    try:
        from app.github_client import GitHubClient
        
        client = GitHubClient()
        
        # Test with the real repository
        owner = "abiodun2025"
        repo = "rag"
        
        logger.info(f"📂 Testing with repository: {owner}/{repo}")
        
        # Note: This would require the app to be installed on the repository
        # For now, we'll just test the client initialization
        logger.info("✅ GitHub client initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ GitHub integration test failed: {e}")


async def test_webhook_simulation():
    """Simulate a webhook payload for testing."""
    
    logger.info("🔄 Testing webhook simulation...")
    
    # Create a sample webhook payload
    webhook_payload = {
        "action": "opened",
        "pull_request": {
            "number": 999,
            "title": "Test: Add code review test file",
            "body": "This is a test PR to demonstrate the AI code review agent",
            "user": {"login": "testuser"},
            "head": {"ref": "feature/code_review_test"},
            "base": {"ref": "main"}
        },
        "repository": {
            "name": "rag",
            "owner": {"login": "abiodun2025"},
            "full_name": "abiodun2025/rag"
        },
        "sender": {"login": "testuser"},
        "installation": {"id": 12345}
    }
    
    logger.info("✅ Webhook payload created successfully")
    logger.info(f"📋 PR #{webhook_payload['pull_request']['number']}: {webhook_payload['pull_request']['title']}")
    
    return webhook_payload


async def main():
    """Run all tests."""
    
    logger.info("🚀 Starting real GitHub integration tests...")
    
    # Test 1: Real code review
    logger.info("\n" + "="*60)
    logger.info("TEST 1: REAL CODE REVIEW")
    logger.info("="*60)
    await test_real_code_review()
    
    # Test 2: GitHub integration
    logger.info("\n" + "="*60)
    logger.info("TEST 2: GITHUB INTEGRATION")
    logger.info("="*60)
    await test_github_integration()
    
    # Test 3: Webhook simulation
    logger.info("\n" + "="*60)
    logger.info("TEST 3: WEBHOOK SIMULATION")
    logger.info("="*60)
    await test_webhook_simulation()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 All tests completed!")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 