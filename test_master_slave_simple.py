#!/usr/bin/env python3
"""
Simple test for Master-Slave Workflow System
"""

import time
from master_agent import MasterAgent

def test_simple_workflow():
    """Test a simple workflow creation."""
    print("🚀 Testing Master-Slave Workflow System")
    print("=" * 50)
    
    try:
        # Initialize master agent
        print("1️⃣ Initializing Master Agent...")
        master = MasterAgent()
        
        # Show agent status
        agent_status = master.get_agent_status()
        print(f"✅ Master Agent initialized with {agent_status['total_agents']} slave agents")
        
        # Create a simple workflow
        print("\n2️⃣ Creating simple PR workflow...")
        workflow_id = master.create_workflow(
            workflow_type="pr_with_report",
            parameters={
                "title": "Test PR from Master Agent",
                "description": "Testing the master-slave system",
                "source_branch": "test-master-agent",
                "target_branch": "main"
            },
            priority=1
        )
        
        print(f"✅ Created workflow: {workflow_id}")
        
        # Monitor for a few seconds
        print("\n3️⃣ Monitoring workflow...")
        for i in range(10):
            status = master.get_workflow_status(workflow_id)
            print(f"   Progress: {status['progress']} - Status: {status['workflow']['status']}")
            
            if status["workflow"]["status"] in ["completed", "failed"]:
                break
            
            time.sleep(2)
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if 'master' in locals():
            master.stop()

if __name__ == "__main__":
    test_simple_workflow()