#!/usr/bin/env python3
"""
Alert System CLI Tool
Command-line interface for managing and testing the alert system.
"""

import asyncio
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, Any
from alert_system import AlertSystem, AlertRule, AlertSeverity, AlertChannel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertCLI:
    """Command-line interface for the alert system."""
    
    def __init__(self):
        self.alert_system = AlertSystem()
    
    async def test_alert(self, rule_id: str, message: str, data: Dict[str, Any] = None):
        """Test sending an alert."""
        try:
            await self.alert_system.trigger_alert(rule_id, message, data or {})
            print(f"✅ Test alert sent for rule: {rule_id}")
        except Exception as e:
            print(f"❌ Failed to send test alert: {e}")
    
    async def list_rules(self):
        """List all configured alert rules."""
        print("\n📋 Alert Rules:")
        print("=" * 80)
        
        for rule_id, rule in self.alert_system.rules.items():
            print(f"Rule ID: {rule_id}")
            print(f"Name: {rule.name}")
            print(f"Description: {rule.description}")
            print(f"Severity: {rule.severity.value}")
            print(f"Channels: {[c.value for c in rule.channels]}")
            print(f"Enabled: {rule.enabled}")
            print(f"Cooldown: {rule.cooldown_minutes} minutes")
            print("-" * 40)
    
    async def add_rule(self, rule_data: Dict[str, Any]):
        """Add a new alert rule."""
        try:
            rule = AlertRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                condition=rule_data["condition"],
                severity=AlertSeverity(rule_data["severity"]),
                channels=[AlertChannel(c) for c in rule_data["channels"]],
                enabled=rule_data.get("enabled", True),
                cooldown_minutes=rule_data.get("cooldown_minutes", 5)
            )
            
            self.alert_system.add_rule(rule)
            print(f"✅ Added alert rule: {rule.name}")
            
        except Exception as e:
            print(f"❌ Failed to add rule: {e}")
    
    async def remove_rule(self, rule_id: str):
        """Remove an alert rule."""
        try:
            self.alert_system.remove_rule(rule_id)
            print(f"✅ Removed alert rule: {rule_id}")
        except Exception as e:
            print(f"❌ Failed to remove rule: {e}")
    
    async def start_monitoring(self):
        """Start the alert monitoring system."""
        try:
            await self.alert_system.start_monitoring()
            print("🚀 Alert monitoring started")
            print("Press Ctrl+C to stop")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await self.alert_system.stop_monitoring()
                print("\n🛑 Alert monitoring stopped")
                
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
    
    async def test_all_channels(self):
        """Test all alert channels with different severities."""
        test_cases = [
            {
                "rule_id": "test_critical",
                "message": "This is a CRITICAL test alert",
                "data": {"test_type": "critical", "timestamp": datetime.now().isoformat()}
            },
            {
                "rule_id": "test_high", 
                "message": "This is a HIGH priority test alert",
                "data": {"test_type": "high", "timestamp": datetime.now().isoformat()}
            },
            {
                "rule_id": "test_medium",
                "message": "This is a MEDIUM priority test alert", 
                "data": {"test_type": "medium", "timestamp": datetime.now().isoformat()}
            },
            {
                "rule_id": "test_low",
                "message": "This is a LOW priority test alert",
                "data": {"test_type": "low", "timestamp": datetime.now().isoformat()}
            }
        ]
        
        print("🧪 Testing all alert channels...")
        
        for test_case in test_cases:
            print(f"\n📤 Testing {test_case['rule_id']}...")
            await self.test_alert(
                test_case["rule_id"],
                test_case["message"], 
                test_case["data"]
            )
            await asyncio.sleep(2)  # Wait between tests
        
        print("\n✅ All channel tests completed")
    
    async def show_status(self):
        """Show alert system status."""
        print("\n📊 Alert System Status:")
        print("=" * 40)
        print(f"Total Rules: {len(self.alert_system.rules)}")
        print(f"Monitoring: {self.alert_system.monitoring}")
        print(f"MCP Server: {self.alert_system.mcp_client.base_url}")
        print(f"Connected: {self.alert_system.mcp_client.connected}")
        print(f"Database: {self.alert_system.storage.db_path}")
        
        # Show recent alerts
        print(f"\n📋 Recent Alerts:")
        print("-" * 40)
        # This would require implementing a method to get recent alerts
        print("(Recent alerts display not implemented yet)")

async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Alert System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test alert command
    test_parser = subparsers.add_parser("test", help="Test an alert")
    test_parser.add_argument("rule_id", help="Alert rule ID to test")
    test_parser.add_argument("message", help="Alert message")
    test_parser.add_argument("--data", help="JSON data for the alert", default="{}")
    
    # List rules command
    subparsers.add_parser("list", help="List all alert rules")
    
    # Add rule command
    add_parser = subparsers.add_parser("add", help="Add a new alert rule")
    add_parser.add_argument("--file", help="JSON file with rule definition", required=True)
    
    # Remove rule command
    remove_parser = subparsers.add_parser("remove", help="Remove an alert rule")
    remove_parser.add_argument("rule_id", help="Rule ID to remove")
    
    # Start monitoring command
    subparsers.add_parser("monitor", help="Start alert monitoring")
    
    # Test all channels command
    subparsers.add_parser("test-all", help="Test all alert channels")
    
    # Status command
    subparsers.add_parser("status", help="Show alert system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AlertCLI()
    
    try:
        if args.command == "test":
            data = json.loads(args.data) if args.data else {}
            await cli.test_alert(args.rule_id, args.message, data)
            
        elif args.command == "list":
            await cli.list_rules()
            
        elif args.command == "add":
            with open(args.file, 'r') as f:
                rule_data = json.load(f)
            await cli.add_rule(rule_data)
            
        elif args.command == "remove":
            await cli.remove_rule(args.rule_id)
            
        elif args.command == "monitor":
            await cli.start_monitoring()
            
        elif args.command == "test-all":
            await cli.test_all_channels()
            
        elif args.command == "status":
            await cli.show_status()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 