#!/usr/bin/env python3
"""
Quick Test for Alert System
Simple test to verify basic functionality.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alert_system import AlertSystem

async def quick_test():
    """Quick test of alert system functionality."""
    print("🚀 Quick Alert System Test")
    print("=" * 40)
    
    try:
        # 1. Initialize alert system
        print("1. Initializing alert system...")
        alert_system = AlertSystem()
        print("   ✅ Alert system initialized")
        
        # 2. Test MCP connection
        print("2. Testing MCP connection...")
        connected = await alert_system.mcp_client.connect()
        if connected:
            print("   ✅ MCP server connected")
        else:
            print("   ⚠️  MCP server not connected (continuing anyway)")
        
        # 3. Check alert rules
        print("3. Checking alert rules...")
        rule_count = len(alert_system.rules)
        print(f"   ✅ {rule_count} alert rules loaded")
        
        # 4. Test email alert
        print("4. Testing email alert...")
        await alert_system.trigger_alert(
            "pr_creation_success",
            "Quick test alert from alert system",
            {
                "test_type": "quick_test",
                "timestamp": datetime.now().isoformat(),
                "message": "This is a test alert to verify the system is working"
            }
        )
        print("   ✅ Email alert sent")
        
        # 5. Test storage
        print("5. Testing alert storage...")
        recent_alerts = alert_system.storage.get_recent_alerts("pr_creation_success", 5)
        print(f"   ✅ {len(recent_alerts)} recent alerts found in storage")
        
        # 6. Test different severity levels
        print("6. Testing severity levels...")
        test_severities = ["pr_creation_success", "workflow_timeout", "agent_blocked"]
        for rule_id in test_severities:
            if rule_id in alert_system.rules:
                await alert_system.trigger_alert(
                    rule_id,
                    f"Test {rule_id} alert",
                    {"test": True, "severity": rule_id}
                )
                print(f"   ✅ {rule_id} alert sent")
        
        print("\n🎉 Quick test completed successfully!")
        print("Check your email/Slack for test alerts.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Check that:")
        print("1. MCP server is running on port 5000")
        print("2. Environment variables are set (ALERT_EMAIL, etc.)")
        print("3. Email/Slack credentials are configured")

if __name__ == "__main__":
    asyncio.run(quick_test()) 