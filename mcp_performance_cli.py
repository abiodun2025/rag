#!/usr/bin/env python3
"""
MCP Performance Testing CLI
Interactive command-line interface for testing MCP server performance
"""

import asyncio
import sys
import argparse
from mcp_performance_agent import MCPPerformanceAgent

async def interactive_mode():
    """Run interactive CLI mode"""
    print("🚀 MCP Performance Testing Agent")
    print("=" * 50)
    
    # Get MCP server URL
    default_url = "http://127.0.0.1:5000"
    server_url = input(f"Enter MCP server URL (default: {default_url}): ").strip()
    if not server_url:
        server_url = default_url
    
    agent = MCPPerformanceAgent(server_url)
    
    try:
        # Check server health
        print(f"\n🔍 Checking server health at {server_url}...")
        if not await agent.check_server_health():
            print("❌ Server is not available. Please ensure your MCP server is running.")
            return
        
        print("✅ Server is healthy!")
        
        while True:
            print("\n" + "=" * 50)
            print("📋 Available Commands:")
            print("1. Quick test (5 iterations each)")
            print("2. Standard test (10 iterations each)")
            print("3. Stress test (20 iterations each)")
            print("4. Test specific workflow")
            print("5. Check available tools")
            print("6. Exit")
            print("=" * 50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                print("\n🧪 Running quick performance test...")
                await run_quick_test(agent)
                
            elif choice == "2":
                print("\n🧪 Running standard performance test...")
                await run_standard_test(agent)
                
            elif choice == "3":
                print("\n🧪 Running stress test...")
                await run_stress_test(agent)
                
            elif choice == "4":
                await run_specific_workflow_test(agent)
                
            elif choice == "5":
                await check_available_tools(agent)
                
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await agent.close()

async def run_quick_test(agent):
    """Run quick performance test"""
    from mcp_performance_agent import MCPPerformanceAgent
    
    # Create a custom agent with quick test parameters
    quick_agent = MCPPerformanceAgent(agent.mcp_server_url)
    
    try:
        # Run tests with fewer iterations
        test_suites = [
            ("count_r", await quick_agent.test_count_r_workflow(5)),
            ("desktop", await quick_agent.test_desktop_workflow(3)),
            ("gmail", await quick_agent.test_gmail_workflow(2)),
            ("email", await quick_agent.test_email_workflow(2))
        ]
        
        all_results = []
        for suite_name, results in test_suites:
            all_results.extend(results)
        
        tools = await quick_agent.get_available_tools()
        report = quick_agent.generate_performance_report(all_results, tools)
        quick_agent.print_performance_report(report)
        
    finally:
        await quick_agent.close()

async def run_standard_test(agent):
    """Run standard performance test"""
    report = await agent.run_comprehensive_test()
    
    if "error" in report:
        print(f"❌ {report['error']}")
        return
    
    agent.print_performance_report(report)

async def run_stress_test(agent):
    """Run stress test with high iterations"""
    print("⚠️  Running stress test with high load...")
    
    stress_agent = MCPPerformanceAgent(agent.mcp_server_url)
    
    try:
        # Run tests with high iterations
        test_suites = [
            ("count_r", await stress_agent.test_count_r_workflow(30)),
            ("desktop", await stress_agent.test_desktop_workflow(15)),
            ("gmail", await stress_agent.test_gmail_workflow(10)),
            ("email", await stress_agent.test_email_workflow(8))
        ]
        
        all_results = []
        for suite_name, results in test_suites:
            all_results.extend(results)
        
        tools = await stress_agent.get_available_tools()
        report = stress_agent.generate_performance_report(all_results, tools)
        stress_agent.print_performance_report(report)
        
    finally:
        await stress_agent.close()

async def run_specific_workflow_test(agent):
    """Test a specific workflow"""
    print("\n🔧 Available Workflows:")
    print("1. count_r (Count 'r' letters in words)")
    print("2. desktop (Desktop path and contents)")
    print("3. gmail (Gmail browser operations)")
    print("4. email (Email sending)")
    
    choice = input("\nSelect workflow to test (1-4): ").strip()
    iterations = input("Enter number of iterations (default: 10): ").strip()
    
    try:
        iterations = int(iterations) if iterations else 10
    except ValueError:
        iterations = 10
    
    if choice == "1":
        print(f"\n🧪 Testing count_r workflow ({iterations} iterations)...")
        results = await agent.test_count_r_workflow(iterations)
    elif choice == "2":
        print(f"\n🧪 Testing desktop workflow ({iterations} iterations)...")
        results = await agent.test_desktop_workflow(iterations)
    elif choice == "3":
        print(f"\n🧪 Testing gmail workflow ({iterations} iterations)...")
        results = await agent.test_gmail_workflow(iterations)
    elif choice == "4":
        print(f"\n🧪 Testing email workflow ({iterations} iterations)...")
        results = await agent.test_email_workflow(iterations)
    else:
        print("❌ Invalid choice")
        return
    
    # Generate report for this specific test
    tools = await agent.get_available_tools()
    report = agent.generate_performance_report(results, tools)
    agent.print_performance_report(report)

async def check_available_tools(agent):
    """Check and display available tools"""
    print("\n🔍 Checking available tools...")
    tools = await agent.get_available_tools()
    
    if tools:
        print(f"\n✅ Found {len(tools)} tools:")
        for i, tool in enumerate(tools, 1):
            tool_name = tool.get('name', 'unknown')
            tool_desc = tool.get('description', 'No description')
            print(f"  {i}. {tool_name}: {tool_desc}")
    else:
        print("❌ No tools found or error getting tools")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP Performance Testing Agent")
    parser.add_argument("--url", default="http://127.0.0.1:5000", 
                       help="MCP server URL (default: http://127.0.0.1:5000)")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick test and exit")
    parser.add_argument("--standard", action="store_true", 
                       help="Run standard test and exit")
    parser.add_argument("--stress", action="store_true", 
                       help="Run stress test and exit")
    parser.add_argument("--tools", action="store_true", 
                       help="List available tools and exit")
    
    args = parser.parse_args()
    
    agent = MCPPerformanceAgent(args.url)
    
    try:
        if args.tools:
            await check_available_tools(agent)
        elif args.quick:
            await run_quick_test(agent)
        elif args.standard:
            await run_standard_test(agent)
        elif args.stress:
            await run_stress_test(agent)
        else:
            await interactive_mode()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main()) 