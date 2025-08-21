#!/usr/bin/env python3
"""
Test script to demonstrate the cybersecurity flow in the Smart Master Agent.
This shows how the system automatically identifies cybersecurity intents and routes them.
"""

import asyncio
import logging
from agent.smart_master_agent import smart_master_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cybersecurity_flow():
    """Test the cybersecurity flow in the smart master agent."""
    
    print("🔒 Testing Cybersecurity Flow in Smart Master Agent")
    print("=" * 60)
    
    # Test cases for different cybersecurity intents
    test_cases = [
        # Dependency vulnerability scanning
        "scan dependencies for vulnerabilities in my project",
        "check packages for CVEs",
        "audit dependencies for security issues",
        
        # SAST scanning
        "perform SAST security analysis on my code",
        "run static code analysis for security",
        "scan code for security vulnerabilities",
        
        # License compliance
        "check license compliance in my repository",
        "audit license compliance",
        "verify license compliance",
        
        # Security best practices
        "check security best practices in my code",
        "audit security standards",
        "review security guidelines",
        
        # Pre-merge security gates
        "check pre-merge security gates",
        "verify pre-commit security checks",
        "block PRs with security issues",
        
        # Security metrics tracking
        "track security metrics over time",
        "monitor security improvements",
        "measure security progress",
        
        # Comprehensive cybersecurity scan
        "perform comprehensive cybersecurity scan",
        "run full security audit",
        "complete security analysis",
        
        # Secrets detection
        "scan for secrets in my files",
        "check for vulnerabilities in my directory",
        "audit for security issues in my project",
        
        # GitHub coverage with security
        "analyze PR coverage for security",
        "check repository coverage",
        "review test coverage"
    ]
    
    session_id = "test_cybersecurity_session"
    user_id = "test_user"
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_message}")
        print("-" * 50)
        
        try:
            # Process the message through the smart master agent
            result = await smart_master_agent.process_message(test_message, session_id, user_id)
            
            # Display results
            intent = result["intent_analysis"]["intent"]
            confidence = result["intent_analysis"]["confidence"]
            extracted_data = result["intent_analysis"]["extracted_data"]
            execution_result = result["execution_result"]
            
            print(f"🎯 Intent: {intent}")
            print(f"📊 Confidence: {confidence:.2f}")
            print(f"🔍 Extracted Data: {extracted_data}")
            print(f"✅ Execution Result: {execution_result.get('action', 'Unknown')}")
            print(f"📝 Note: {execution_result.get('note', 'No note')}")
            
            # Show specific cybersecurity features if applicable
            if intent == "cybersecurity_scan":
                scan_type = extracted_data.get("scan_type", "comprehensive")
                print(f"🔒 Scan Type: {scan_type}")
                
                if "dependency" in scan_type:
                    print("   📦 Will scan dependencies for vulnerabilities")
                if "sast" in scan_type:
                    print("   🔍 Will perform SAST static analysis")
                if "license" in scan_type:
                    print("   📜 Will check license compliance")
                if "best_practices" in scan_type:
                    print("   ✅ Will check security best practices")
                if "pre_merge" in scan_type:
                    print("   🚦 Will check pre-merge security gates")
                if "metrics" in scan_type:
                    print("   📊 Will track security metrics")
                    
            elif intent == "secrets_detection":
                scan_type = extracted_data.get("scan_type", "comprehensive")
                target = extracted_data.get("target", ".")
                print(f"🔐 Scan Type: {scan_type}")
                print(f"🎯 Target: {target}")
                
            elif intent == "github_coverage":
                analysis_type = extracted_data.get("analysis_type", "repository")
                pr_number = extracted_data.get("pr_number")
                branch = extracted_data.get("branch", "main")
                print(f"🔍 Analysis Type: {analysis_type}")
                if pr_number:
                    print(f"📝 PR Number: {pr_number}")
                print(f"🌿 Branch: {branch}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("🎉 Cybersecurity Flow Testing Completed!")
    print("\n📋 Summary of Cybersecurity Features Added:")
    print("• Dependency vulnerability scanning")
    print("• SAST (Static Analysis Security Testing)")
    print("• License compliance checking")
    print("• Security best practices validation")
    print("• Pre-merge security gates")
    print("• Security metrics tracking")
    print("• Comprehensive cybersecurity scanning")
    print("• Secrets detection integration")
    print("• GitHub coverage with security focus")
    
    print("\n🚀 The system now automatically:")
    print("• Identifies cybersecurity-related requests")
    print("• Routes them to appropriate security handlers")
    print("• Performs targeted security scans")
    print("• Generates comprehensive security reports")
    print("• Provides risk assessments and recommendations")
    print("• Integrates with existing MCP tools")

if __name__ == "__main__":
    asyncio.run(test_cybersecurity_flow())











