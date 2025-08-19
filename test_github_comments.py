#!/usr/bin/env python3
"""
Test script to demonstrate GitHub-style comments from the AI agent.
"""

import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_github_comments():
    """Demonstrate how the AI agent would comment on GitHub PRs."""
    
    print("🤖 GITHUB AI CODE REVIEW AGENT - SENIOR DEVELOPER COMMENTS")
    print("=" * 70)
    
    # Sample problematic code that would trigger real GitHub comments
    problematic_code = '''
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
    
    return result
'''
    
    print("📝 CODE BEING REVIEWED:")
    print("-" * 40)
    print(problematic_code)
    print("-" * 40)
    
    print("\n🔍 AI SENIOR DEVELOPER COMMENTS:")
    print("=" * 70)
    
    # Simulate the AI review comments as they would appear on GitHub
    github_comments = [
        {
            "line": 8,
            "body": "🚨 **CRITICAL SECURITY ISSUE**: Using `eval()` is extremely dangerous and should never be used with user input. This opens your application to code injection attacks.\n\n**Recommendation**: Replace with `ast.literal_eval()` for safe evaluation of literals, or use `json.loads()` for JSON data.\n\n```python\n# Instead of: result = eval(user_input)\n# Use: result = ast.literal_eval(user_input)  # for literals\n# Or: result = json.loads(user_input)  # for JSON\n```",
            "type": "error"
        },
        {
            "line": 11,
            "body": "🔐 **SECURITY RISK**: Hardcoded API keys and passwords in source code is a major security vulnerability. These credentials could be exposed in version control.\n\n**Recommendation**: Use environment variables or a secure secrets management system:\n\n```python\nimport os\napi_key = os.getenv('API_KEY')\npassword = os.getenv('PASSWORD')\n```\n\nAlso, consider using a secrets manager like AWS Secrets Manager or HashiCorp Vault for production environments.",
            "type": "error"
        },
        {
            "line": 14,
            "body": "⚠️ **ERROR HANDLING**: This line could raise a `JSONDecodeError` if the input is not valid JSON. Always wrap JSON parsing in try-catch blocks.\n\n**Recommendation**:\n```python\ntry:\n    data = json.loads(user_input)\nexcept json.JSONDecodeError as e:\n    logger.error(f\"Invalid JSON input: {e}\")\n    return {\"error\": \"Invalid JSON format\"}\n```",
            "type": "warning"
        },
        {
            "line": 17,
            "body": "⚡ **PERFORMANCE OPTIMIZATION**: This loop is inefficient and can be replaced with a more Pythonic approach.\n\n**Recommendation**: Use list comprehension or range directly:\n```python\n# Instead of:\nitems = []\nfor i in range(1000):\n    items.append(i)\n\n# Use:\nitems = list(range(1000))\n# Or even better, if you just need the range:\nitems = range(1000)\n```\n\nThis is more readable and performs better.",
            "type": "suggestion"
        },
        {
            "line": 21,
            "body": "🧹 **CODE CLEANUP**: The variable `unused_var` is defined but never used. This creates unnecessary memory allocation and makes the code harder to read.\n\n**Recommendation**: Remove this line entirely. If you need it for future use, add a `# TODO:` comment explaining why it's there.",
            "type": "suggestion"
        },
        {
            "line": 24,
            "body": "🔢 **MAGIC NUMBER**: The number `100` appears without context. This makes the code harder to understand and maintain.\n\n**Recommendation**: Define it as a constant at the top of the file:\n```python\nMAX_DATA_SIZE = 100\n\n# Then use:\nif len(data) > MAX_DATA_SIZE:\n    return {\"status\": \"too large\"}\n```\n\nThis makes the code self-documenting and easier to modify.",
            "type": "suggestion"
        }
    ]
    
    # Display comments as they would appear on GitHub
    for i, comment in enumerate(github_comments, 1):
        print(f"\n💬 **Comment {i}** (Line {comment['line']}):")
        print(f"Type: {comment['type'].upper()}")
        print("-" * 50)
        print(comment['body'])
        print("-" * 50)
    
    print(f"\n📊 **SUMMARY**:")
    print(f"• Total comments: {len(github_comments)}")
    print(f"• Security issues: 2 (Critical)")
    print(f"• Performance issues: 1")
    print(f"• Code quality issues: 3")
    print(f"• Overall assessment: Needs significant improvements for security and maintainability")
    
    print(f"\n🎯 **NEXT STEPS**:")
    print(f"1. Address the critical security issues first (eval() and hardcoded credentials)")
    print(f"2. Add proper error handling for JSON parsing")
    print(f"3. Optimize the inefficient loop")
    print(f"4. Clean up unused variables and magic numbers")
    
    print(f"\n✅ **POSITIVE FEEDBACK**:")
    print(f"• Good use of type hints in function signature")
    print(f"• Clear function documentation")
    print(f"• Logical code structure")


async def test_real_ai_review():
    """Test the actual AI review with the problematic code."""
    
    print("\n" + "=" * 70)
    print("🤖 ACTUAL AI REVIEW RESULTS")
    print("=" * 70)
    
    try:
        from app.code_review_service import CodeReviewService
        
        service = CodeReviewService()
        
        # Create a diff with the problematic code
        diff_content = """
diff --git a/test_function.py b/test_function.py
new file mode 100644
--- /dev/null
+++ b/test_function.py
@@ -0,0 +1,25 @@
+def process_user_data(user_input: str) -> Dict[str, Any]:
+    \"\"\"
+    Process user data without proper validation.
+    This function has several security and best practice issues.
+    \"\"\"
+    # No input validation
+    result = eval(user_input)  # SECURITY ISSUE: eval() is dangerous
+    
+    # Hardcoded credentials - bad practice
+    api_key = \"sk-1234567890abcdef\"
+    password = \"admin123\"
+    
+    # No error handling
+    data = json.loads(user_input)
+    
+    # Inefficient loop
+    items = []
+    for i in range(1000):
+        items.append(i)
+    
+    # Unused variable
+    unused_var = \"this is never used\"
+    
+    # Magic numbers
+    if len(data) > 100:
+        return {\"status\": \"too large\"}
+    
+    return result
"""
        
        result = await service.review_code(
            diff_content=diff_content,
            changed_files=["test_function.py"]
        )
        
        if result["success"]:
            print(f"✅ AI Review completed successfully!")
            print(f"📝 Generated {len(result.get('comments', []))} comments")
            print(f"📋 Summary: {result.get('summary', 'No summary')}")
            
            print(f"\n🔍 DETAILED AI COMMENTS:")
            print("-" * 50)
            
            for i, comment in enumerate(result.get('comments', []), 1):
                print(f"\n💬 Comment {i}:")
                print(f"   Line: {comment.line}")
                print(f"   Issue: {comment.body}")
                print("-" * 30)
        else:
            print(f"❌ AI Review failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def main():
    """Run the demonstration."""
    
    # Show how comments would appear on GitHub
    await demonstrate_github_comments()
    
    # Test the actual AI review
    await test_real_ai_review()
    
    print(f"\n" + "=" * 70)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 70)
    
    print(f"\n💡 **KEY TAKEAWAYS**:")
    print(f"• The AI provides human-like, constructive feedback")
    print(f"• Comments include specific code examples and solutions")
    print(f"• Security issues are prioritized and clearly explained")
    print(f"• Performance and code quality suggestions are practical")
    print(f"• The tone is helpful and educational, like a senior developer")


if __name__ == "__main__":
    asyncio.run(main()) 