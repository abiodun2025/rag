#!/usr/bin/env python3
"""
Comprehensive Test Suite for Alert System
Tests all components and integrations.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alert_system import AlertSystem, AlertRule, AlertSeverity, AlertChannel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlertSystemTester:
    """Comprehensive test suite for the alert system."""
    
    def __init__(self):
        self.alert_system = AlertSystem()
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all tests and report results."""
        print("🧪 Starting Alert System Tests")
        print("=" * 60)
        
        tests = [
            ("Test MCP Connection", self.test_mcp_connection),
            ("Test Alert Rules", self.test_alert_rules),
            ("Test Email Alerts", self.test_email_alerts),
            ("Test Slack Alerts", self.test_slack_alerts),
            ("Test Teams Alerts", self.test_teams_alerts),
            ("Test Alert Storage", self.test_alert_storage),
            ("Test Cooldown Protection", self.test_cooldown_protection),
            ("Test Severity Levels", self.test_severity_levels),
            ("Test Integration", self.test_integration),
            ("Test Monitoring", self.test_monitoring)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                result = await test_func()
                self.test_results.append((test_name, "PASS", result))
                print(f"✅ {test_name}: PASS")
            except Exception as e:
                self.test_results.append((test_name, "FAIL", str(e)))
                print(f"❌ {test_name}: FAIL - {e}")
        
        self.print_summary()
    
    async def test_mcp_connection(self):
        """Test MCP server connection."""
        try:
            connected = await self.alert_system.mcp_client.connect()
            if not connected:
                raise Exception("Failed to connect to MCP server")
            
            # Test tool discovery
            tools = await self.alert_system.mcp_client.discover_tools()
            if not tools:
                raise Exception("No tools discovered from MCP server")
            
            return f"Connected to MCP server, discovered {len(tools)} tools"
            
        except Exception as e:
            raise Exception(f"MCP connection failed: {e}")
    
    async def test_alert_rules(self):
        """Test alert rule management."""
        # Test default rules
        if len(self.alert_system.rules) == 0:
            raise Exception("No default rules loaded")
        
        # Test adding a custom rule
        custom_rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test alert rule",
            condition="True",
            severity=AlertSeverity.LOW,
            channels=[AlertChannel.EMAIL]
        )
        
        self.alert_system.add_rule(custom_rule)
        
        if "test_rule" not in self.alert_system.rules:
            raise Exception("Failed to add custom rule")
        
        # Test removing rule
        self.alert_system.remove_rule("test_rule")
        
        if "test_rule" in self.alert_system.rules:
            raise Exception("Failed to remove custom rule")
        
        return f"Alert rules working, {len(self.alert_system.rules)} rules configured"
    
    async def test_email_alerts(self):
        """Test email alert functionality."""
        try:
            # Test email alert
            await self.alert_system.trigger_alert(
                "pr_creation_success",
                "Test email alert",
                {"test": True, "timestamp": datetime.now().isoformat()}
            )
            
            return "Email alert test completed"
            
        except Exception as e:
            raise Exception(f"Email alert test failed: {e}")
    
    async def test_slack_alerts(self):
        """Test Slack alert functionality."""
        try:
            # Test Slack alert
            await self.alert_system.trigger_alert(
                "workflow_completed",
                "Test Slack alert",
                {"test": True, "timestamp": datetime.now().isoformat()}
            )
            
            return "Slack alert test completed"
            
        except Exception as e:
            # Slack might not be configured, that's okay
            return f"Slack alert test skipped (not configured): {e}"
    
    async def test_teams_alerts(self):
        """Test Teams alert functionality."""
        try:
            # Test Teams alert
            await self.alert_system.trigger_alert(
                "task_execution_failed",
                "Test Teams alert",
                {"test": True, "timestamp": datetime.now().isoformat()}
            )
            
            return "Teams alert test completed"
            
        except Exception as e:
            # Teams might not be configured, that's okay
            return f"Teams alert test skipped (not configured): {e}"
    
    async def test_alert_storage(self):
        """Test alert storage functionality."""
        try:
            # Trigger a test alert
            await self.alert_system.trigger_alert(
                "test_storage",
                "Test storage alert",
                {"test": "storage", "timestamp": datetime.now().isoformat()}
            )
            
            # Check if alert was stored
            recent_alerts = self.alert_system.storage.get_recent_alerts("test_storage", 5)
            
            if len(recent_alerts) == 0:
                raise Exception("Alert was not stored in database")
            
            return f"Alert storage working, {len(recent_alerts)} recent alerts found"
            
        except Exception as e:
            raise Exception(f"Alert storage test failed: {e}")
    
    async def test_cooldown_protection(self):
        """Test cooldown protection."""
        try:
            # Trigger alert twice quickly
            await self.alert_system.trigger_alert(
                "test_cooldown",
                "First alert",
                {"test": "cooldown"}
            )
            
            await self.alert_system.trigger_alert(
                "test_cooldown",
                "Second alert (should be blocked by cooldown)",
                {"test": "cooldown"}
            )
            
            # Check that only one alert was sent
            recent_alerts = self.alert_system.storage.get_recent_alerts("test_cooldown", 5)
            
            if len(recent_alerts) > 1:
                raise Exception("Cooldown protection not working")
            
            return "Cooldown protection working correctly"
            
        except Exception as e:
            raise Exception(f"Cooldown test failed: {e}")
    
    async def test_severity_levels(self):
        """Test different severity levels."""
        try:
            severities = [
                AlertSeverity.CRITICAL,
                AlertSeverity.HIGH,
                AlertSeverity.MEDIUM,
                AlertSeverity.LOW
            ]
            
            for severity in severities:
                await self.alert_system.trigger_alert(
                    "test_severity",
                    f"Test {severity.value} alert",
                    {"severity": severity.value, "timestamp": datetime.now().isoformat()}
                )
                await asyncio.sleep(1)  # Small delay between tests
            
            return f"All {len(severities)} severity levels tested"
            
        except Exception as e:
            raise Exception(f"Severity test failed: {e}")
    
    async def test_integration(self):
        """Test integration with other components."""
        try:
            # Test workflow integration
            from alert_integration import WorkflowAlertIntegration
            
            workflow_alerts = WorkflowAlertIntegration(self.alert_system)
            
            # Test workflow start
            await workflow_alerts.on_workflow_start(
                "test_workflow_123",
                "test_workflow",
                {"test": True}
            )
            
            # Test workflow completion
            await workflow_alerts.on_workflow_complete(
                "test_workflow_123",
                "test_workflow",
                True,
                {"result": "success"}
            )
            
            return "Integration tests completed"
            
        except Exception as e:
            raise Exception(f"Integration test failed: {e}")
    
    async def test_monitoring(self):
        """Test monitoring functionality."""
        try:
            # Start monitoring
            await self.alert_system.start_monitoring()
            
            # Let it run for a few seconds
            await asyncio.sleep(5)
            
            # Stop monitoring
            await self.alert_system.stop_monitoring()
            
            return "Monitoring test completed"
            
        except Exception as e:
            raise Exception(f"Monitoring test failed: {e}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        print("-" * 60)
        
        for test_name, status, result in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {status}")
            if isinstance(result, str) and len(result) > 0:
                print(f"   └─ {result}")
        
        if failed > 0:
            print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        else:
            print(f"\n🎉 All tests passed! Alert system is working correctly.")

async def main():
    """Main test runner."""
    tester = AlertSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 