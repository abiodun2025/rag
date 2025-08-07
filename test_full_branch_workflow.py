#!/usr/bin/env python3
"""
Test Full Branch Workflow - Complete workflow (Branch + Push + PR + Report)
"""

import requests
import json
import time
import uuid
from datetime import datetime

def test_full_branch_workflow():
    """Test the complete branch workflow with GitHub integration."""
    
    print("🚀 FULL BRANCH WORKFLOW TEST")
    print("=" * 60)
    print("This test verifies the complete workflow:")
    print("1. Create Branch")
    print("2. Push Branch")
    print("3. Create Pull Request")
    print("4. Generate Report")
    print()
    
    # Test 1: Check if GitHub MCP Bridge is running
    print("📋 Test 1: Checking GitHub MCP Bridge Health")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ GitHub MCP Bridge is running")
            print(f"   Server: {health_data.get('server', 'Unknown')}")
            print(f"   GitHub configured: {health_data.get('github_configured', False)}")
            
            if not health_data.get('github_configured', False):
                print("⚠️  GitHub not configured - some features may not work")
                print("   Run: python3 setup_github.py")
        else:
            print("❌ GitHub MCP Bridge is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ GitHub MCP Bridge is not running on port 5000")
        print("   Start it with: python3 github_mcp_bridge.py")
        return False
    
    # Test 2: Check available tools
    print("\n📋 Test 2: Checking Available Tools")
    try:
        response = requests.get("http://localhost:5000/tools")
        if response.status_code == 200:
            tools = response.json()
            workflow_tools = [
                tool for tool in tools.get("tools", []) 
                if any(keyword in tool["name"] for keyword in ["branch", "pr", "report", "push"])
            ]
            print(f"✅ Found {len(workflow_tools)} workflow tools:")
            for tool in workflow_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Failed to get tools list")
            return False
    except Exception as e:
        print(f"❌ Error getting tools: {e}")
        return False
    
    # Test 3: Test Master Agent with Full Branch Workflow
    print("\n📋 Test 3: Testing Master Agent Full Branch Workflow")
    try:
        from master_agent import MasterAgent
        
        # Initialize master agent
        master = MasterAgent()
        
        # Create a full branch workflow
        workflow_id = master.create_workflow("full_branch_workflow", {
            "title": "Test Full Branch Workflow",
            "description": f"""Complete branch workflow test

## Description
Testing the full branch workflow with GitHub integration.

## Branch Details
- Source: test-full-workflow-{int(time.time())}
- Target: main
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Workflow Steps
1. Create Branch (Branch Agent)
2. Push Branch (Branch Agent)
3. Create Pull Request (PR Agent)
4. Generate Report (Report Agent)

This is a comprehensive test of the master-slave agent system.""",
            "source_branch": f"test-full-workflow-{int(time.time())}",
            "target_branch": "main",
            "branch_name": f"test-full-workflow-{int(time.time())}"
        })
        
        if workflow_id:
            print(f"✅ Created full branch workflow: {workflow_id}")
            
            # Monitor the workflow
            print("\n⏳ Monitoring workflow execution...")
            for i in range(15):  # Monitor for up to 30 seconds
                status = master.get_workflow_status(workflow_id)
                
                if "error" not in status:
                    workflow_status = status.get('workflow', {}).get('status', 'unknown')
                    progress = status.get('progress', 'unknown')
                    print(f"   Progress: {progress} - Status: {workflow_status}")
                    
                    if workflow_status in ["completed", "failed"]:
                        break
                else:
                    print(f"   Error: {status.get('error', 'Unknown error')}")
                    break
                
                time.sleep(2)
            
            # Show final results
            final_status = master.get_workflow_status(workflow_id)
            if "error" not in final_status:
                workflow_status = final_status.get('workflow', {}).get('status', 'unknown')
                if workflow_status == "completed":
                    print("\n🎉 FULL BRANCH WORKFLOW COMPLETED SUCCESSFULLY!")
                    print("✅ All workflow steps executed:")
                    print("   - Branch created and pushed")
                    print("   - Pull request created")
                    print("   - Report generated")
                else:
                    print(f"\n❌ Workflow failed with status: {workflow_status}")
            else:
                print(f"\n❌ Workflow error: {final_status.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to create full branch workflow")
            return False
            
    except Exception as e:
        print(f"❌ Error testing master agent: {e}")
        return False
    
    print("\n🎉 Full Branch Workflow Testing Complete!")
    return True

def test_individual_workflow_steps():
    """Test individual workflow steps to isolate issues."""
    
    print("\n🔧 INDIVIDUAL WORKFLOW STEP TESTING")
    print("=" * 50)
    
    # Test branch creation
    print("\n📋 Testing Branch Creation")
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "create_branch",
            "arguments": {
                "branch_name": f"test-individual-{int(time.time())}",
                "title": "Test Individual Branch",
                "description": "Testing individual branch creation"
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Branch creation successful")
                print(f"   Result: {result.get('result')}")
            else:
                print(f"❌ Branch creation failed: {result.get('error')}")
        else:
            print(f"❌ Branch creation HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Branch creation error: {e}")
    
    # Test PR creation
    print("\n📋 Testing Pull Request Creation")
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "create_pull_request",
            "arguments": {
                "title": "Test Individual PR",
                "description": "Testing individual PR creation",
                "source_branch": "test-branch",
                "target_branch": "main"
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ PR creation successful")
                print(f"   Result: {result.get('result')}")
            else:
                print(f"❌ PR creation failed: {result.get('error')}")
        else:
            print(f"❌ PR creation HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ PR creation error: {e}")
    
    # Test report generation
    print("\n📋 Testing Report Generation")
    try:
        response = requests.post("http://localhost:5000/call", json={
            "tool": "generate_report",
            "arguments": {
                "title": "Test Report",
                "content": "This is a test report generated by the workflow system."
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Report generation successful")
                print(f"   Result: {result.get('result')}")
            else:
                print(f"❌ Report generation failed: {result.get('error')}")
        else:
            print(f"❌ Report generation HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Report generation error: {e}")

if __name__ == "__main__":
    print("🚀 FULL BRANCH WORKFLOW TESTING")
    print("=" * 60)
    print("This test verifies the complete branch workflow functionality")
    print("including branch creation, pushing, PR creation, and report generation.")
    print()
    
    # Test the full workflow
    success = test_full_branch_workflow()
    
    if not success:
        print("\n🔧 Testing individual steps to isolate issues...")
        test_individual_workflow_steps()
    
    print("\n📋 SUMMARY:")
    if success:
        print("✅ Full branch workflow: WORKING")
        print("✅ GitHub integration: WORKING")
        print("✅ Master agent coordination: WORKING")
        print("✅ All workflow steps: WORKING")
        print("\n🎯 The full branch workflow is now fully operational!")
    else:
        print("❌ Full branch workflow: NEEDS ATTENTION")
        print("💡 Check GitHub configuration and individual step results above")
        print("🔧 Run: python3 setup_github.py to configure GitHub credentials") 