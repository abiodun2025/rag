#!/usr/bin/env python3
"""
Secrets Detection Agent CLI
Command-line interface for the secrets detection agent.
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from agent.secrets_detection_agent import SecretsDetectionAgent

def print_banner():
    """Print the CLI banner."""
    print("🔐 Secrets Detection Agent CLI")
    print("=" * 50)
    print("🔍 Scans files and directories for secrets, API keys, passwords, and tokens")
    print("🔗 Uses MCP server tools for comprehensive security scanning")
    print("=" * 50)

def print_help():
    """Print help information."""
    print("\n📖 Available Commands:")
    print("  scan-file <file_path>           - Scan a specific file for secrets")
    print("  scan-dir <directory_path>       - Scan a directory for secrets")
    print("  scan-env <directory_path>       - Scan environment files for secrets")
    print("  detect-api-keys <file_path>     - Detect API keys in a file")
    print("  detect-passwords <file_path>    - Detect passwords in a file")
    print("  detect-tokens <file_path>       - Detect tokens in a file")
    print("  comprehensive <directory_path>  - Run comprehensive security scan")
    print("  info                            - Show agent information")
    print("  help                            - Show this help message")
    print("  exit                            - Exit the CLI")
    print("\n💡 Examples:")
    print("  scan-file .env                  - Scan .env file for secrets")
    print("  scan-dir .                      - Scan current directory")
    print("  comprehensive .                 - Run full security scan")
    print("  detect-api-keys config.json     - Check for API keys in config")

async def scan_file(agent: SecretsDetectionAgent, file_path: str):
    """Scan a file for secrets."""
    print(f"🔍 Scanning file: {file_path}")
    
    result = await agent.scan_file_for_secrets(file_path)
    
    if result["success"]:
        print(f"✅ Scan completed: {result['results']['scan_summary']}")
        print(f"📊 Found {result['results']['total_secrets']} potential secrets")
        
        if result['results']['secrets_found']:
            print("\n🔍 Secrets found:")
            for i, secret in enumerate(result['results']['secrets_found'], 1):
                print(f"  {i}. Pattern: {secret['pattern']}")
                print(f"     Value: {secret['value']}")
                print(f"     Line: {secret['line_number']}")
                print(f"     Context: {secret['context']}")
                print()
    else:
        print(f"❌ Scan failed: {result['error']}")

async def scan_directory(agent: SecretsDetectionAgent, directory_path: str):
    """Scan a directory for secrets."""
    print(f"🔍 Scanning directory: {directory_path}")
    
    result = await agent.scan_directory_for_secrets(directory_path)
    
    if result["success"]:
        print(f"✅ Scan completed: {result['results']['scan_summary']}")
        print(f"📊 Scanned {result['results']['files_scanned']} files")
        print(f"🔍 Found secrets in {result['results']['files_with_secrets']} files")
        print(f"🚨 Total secrets found: {result['results']['total_secrets_found']}")
        
        if result['results']['scan_results']:
            print("\n🔍 Files with secrets:")
            for file_result in result['results']['scan_results']:
                print(f"  📁 {file_result['file_name']}")
                print(f"     Secrets: {file_result['secret_count']}")
                print(f"     Path: {file_result['file_path']}")
                print()
    else:
        print(f"❌ Scan failed: {result['error']}")

async def scan_env_files(agent: SecretsDetectionAgent, directory_path: str):
    """Scan environment files for secrets."""
    print(f"🔍 Scanning environment files in: {directory_path}")
    
    result = await agent.scan_env_files(directory_path)
    
    if result["success"]:
        print(f"✅ Scan completed: {result['results']['scan_summary']}")
        print(f"📊 Found {result['results']['total_env_files']} environment files")
        print(f"🚨 Total secrets found: {result['results']['total_secrets_found']}")
        
        if result['results']['env_files_found']:
            print("\n🔍 Environment files with secrets:")
            for env_file in result['results']['env_files_found']:
                print(f"  📁 {env_file['file_name']}")
                print(f"     Secrets: {env_file['secret_count']}")
                print(f"     Path: {env_file['file_path']}")
                print()
    else:
        print(f"❌ Scan failed: {result['error']}")

async def detect_api_keys(agent: SecretsDetectionAgent, file_path: str):
    """Detect API keys in a file."""
    print(f"🔑 Detecting API keys in: {file_path}")
    
    result = await agent.detect_api_keys(file_path=file_path)
    
    if result["success"]:
        print(f"✅ Detection completed: {result['results']['scan_summary']}")
        print(f"📊 Found {result['results']['total_api_keys']} potential API keys")
        
        if result['results']['api_keys_found']:
            print("\n🔑 API keys found:")
            for i, api_key in enumerate(result['results']['api_keys_found'], 1):
                print(f"  {i}. Pattern: {api_key['pattern']}")
                print(f"     Value: {api_key['value']}")
                print(f"     Line: {api_key['line_number']}")
                print(f"     Context: {api_key['context']}")
                print()
    else:
        print(f"❌ Detection failed: {result['error']}")

async def detect_passwords(agent: SecretsDetectionAgent, file_path: str):
    """Detect passwords in a file."""
    print(f"🔒 Detecting passwords in: {file_path}")
    
    result = await agent.detect_passwords(file_path=file_path)
    
    if result["success"]:
        print(f"✅ Detection completed: {result['results']['scan_summary']}")
        print(f"📊 Found {result['results']['total_passwords']} potential passwords")
        
        if result['results']['passwords_found']:
            print("\n🔒 Passwords found:")
            for i, password in enumerate(result['results']['passwords_found'], 1):
                print(f"  {i}. Pattern: {password['pattern']}")
                print(f"     Value: {password['value']}")
                print(f"     Line: {password['line_number']}")
                print(f"     Context: {password['context']}")
                print()
    else:
        print(f"❌ Detection failed: {result['error']}")

async def detect_tokens(agent: SecretsDetectionAgent, file_path: str):
    """Detect tokens in a file."""
    print(f"🎫 Detecting tokens in: {file_path}")
    
    result = await agent.detect_tokens(file_path=file_path)
    
    if result["success"]:
        print(f"✅ Detection completed: {result['results']['scan_summary']}")
        print(f"📊 Found {result['results']['total_tokens']} potential tokens")
        
        if result['results']['tokens_found']:
            print("\n🎫 Tokens found:")
            for i, token in enumerate(result['results']['tokens_found'], 1):
                print(f"  {i}. Pattern: {token['pattern']}")
                print(f"     Value: {token['value']}")
                print(f"     Line: {token['line_number']}")
                print(f"     Context: {token['context']}")
                print()
    else:
        print(f"❌ Detection failed: {result['error']}")

async def comprehensive_scan(agent: SecretsDetectionAgent, directory_path: str):
    """Run a comprehensive security scan."""
    print(f"🚀 Running comprehensive security scan: {directory_path}")
    print("This may take a few moments...")
    
    result = await agent.run_comprehensive_scan(directory_path)
    
    if result["success"]:
        print("✅ Comprehensive scan completed successfully!")
        print(f"📊 Summary: {result['summary']}")
        
        # Show detailed results
        if 'results' in result:
            print("\n📋 Detailed Results:")
            
            # Directory scan results
            if 'directory_scan' in result['results']:
                dir_scan = result['results']['directory_scan']
                if dir_scan.get('success'):
                    print(f"  📁 Directory Scan: {dir_scan.get('results', {}).get('scan_summary', 'N/A')}")
                else:
                    print(f"  ❌ Directory Scan: {dir_scan.get('error', 'N/A')}")
            
            # Env scan results
            if 'env_scan' in result['results']:
                env_scan = result['results']['env_scan']
                if env_scan.get('success'):
                    print(f"  🔧 Env Files Scan: {env_scan.get('results', {}).get('scan_summary', 'N/A')}")
                else:
                    print(f"  ❌ Env Files Scan: {env_scan.get('error', 'N/A')}")
            
            # Security report
            if 'security_report' in result['results']:
                sec_report = result['results']['security_report']
                if sec_report.get('success'):
                    report = sec_report.get('report', {})
                    if 'risk_assessment' in report:
                        risk = report['risk_assessment']
                        print(f"  🚨 Risk Assessment: {risk.get('risk_level', 'N/A')} (Score: {risk.get('risk_score', 'N/A')})")
                    
                    if 'recommendations' in report:
                        recs = report['recommendations']
                        print(f"  💡 Recommendations: {len(recs)} provided")
                        for i, rec in enumerate(recs[:3], 1):  # Show first 3
                            print(f"     {i}. {rec.get('recommendation', 'N/A')}")
                else:
                    print(f"  ❌ Security Report: {sec_report.get('error', 'N/A')}")
    else:
        print(f"❌ Comprehensive scan failed: {result['error']}")

def show_agent_info(agent: SecretsDetectionAgent):
    """Show agent information."""
    info = agent.get_agent_info()
    
    print(f"🤖 Agent Information:")
    print(f"  Name: {info['agent_name']}")
    print(f"  Version: {info['version']}")
    print(f"  Description: {info['description']}")
    print(f"  MCP Server: {info['mcp_server_url']}")
    print(f"  Timestamp: {info['timestamp']}")
    
    print(f"\n🔧 Capabilities:")
    for capability in info['capabilities']:
        print(f"  • {capability}")

async def interactive_mode(agent: SecretsDetectionAgent):
    """Run the CLI in interactive mode."""
    print_banner()
    print_help()
    
    while True:
        try:
            command = input("\n🔐 Secrets Agent> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if command.lower() in ['help', 'h']:
                print_help()
                continue
            
            if command.lower() in ['info', 'i']:
                show_agent_info(agent)
                continue
            
            # Parse command
            parts = command.split()
            if len(parts) < 2:
                print("❌ Invalid command. Use 'help' for available commands.")
                continue
            
            action = parts[0].lower()
            target = parts[1]
            
            # Execute commands
            if action == "scan-file":
                await scan_file(agent, target)
            elif action == "scan-dir":
                await scan_directory(agent, target)
            elif action == "scan-env":
                await scan_env_files(agent, target)
            elif action == "detect-api-keys":
                await detect_api_keys(agent, target)
            elif action == "detect-passwords":
                await detect_passwords(agent, target)
            elif action == "detect-tokens":
                await detect_tokens(agent, target)
            elif action == "comprehensive":
                await comprehensive_scan(agent, target)
            else:
                print(f"❌ Unknown command: {action}")
                print("Use 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Secrets Detection Agent CLI")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("target", nargs="?", help="Target file or directory")
    parser.add_argument("--mcp-server", default="http://127.0.0.1:5000", help="MCP server URL")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = SecretsDetectionAgent(args.mcp_server)
    
    if args.interactive or (not args.command and not args.target):
        await interactive_mode(agent)
    elif args.command and args.target:
        # Single command execution
        if args.command == "scan-file":
            await scan_file(agent, args.target)
        elif args.command == "scan-dir":
            await scan_directory(agent, args.target)
        elif args.command == "scan-env":
            await scan_env_files(agent, args.target)
        elif args.command == "detect-api-keys":
            await detect_api_keys(agent, args.target)
        elif args.command == "detect-passwords":
            await detect_passwords(agent, args.target)
        elif args.command == "detect-tokens":
            await detect_tokens(agent, args.target)
        elif args.command == "comprehensive":
            await comprehensive_scan(agent, args.target)
        else:
            print(f"❌ Unknown command: {args.command}")
            print("Use --help for available commands.")
    else:
        print("❌ Invalid arguments.")
        print("Use --help for usage information or --interactive for interactive mode.")

if __name__ == "__main__":
    asyncio.run(main())
