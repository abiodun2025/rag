#!/usr/bin/env python3
"""
GitHub Code Review Agent CLI
============================

A dedicated command-line interface for reviewing GitHub repositories.
Version: 1.0.0
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_review_agent import GitHubReviewAgent

class CodeReviewCLI:
    """Command-line interface for GitHub code review."""
    
    def __init__(self):
        self.agent = GitHubReviewAgent()
        self.version = "1.0.0"
    
    def print_banner(self):
        """Print the CLI banner."""
        print("=" * 60)
        print("🔍 GitHub Code Review Agent CLI v" + self.version)
        print("=" * 60)
        print("Review any GitHub repository with comprehensive analysis!")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 60)
    
    def print_help(self):
        """Print help information."""
        print("\n📋 Available Commands:")
        print("  review <repo_url> [options]  - Review a GitHub repository")
        print("  help                         - Show this help")
        print("  version                      - Show version information")
        print("  exit                         - Exit the CLI")
        print("\n📝 Examples:")
        print("  review https://github.com/owner/repo")
        print("  review https://github.com/owner/repo --type security")
        print("  review https://github.com/owner/repo --format detailed")
        print("  review https://github.com/owner/repo --no-clone")
        print("\n🔧 Options:")
        print("  --type <type>               - Review type: full, security, performance, style")
        print("  --format <format>           - Output format: summary, detailed, json")
        print("  --no-clone                  - Don't clone locally (faster but less thorough)")
        print("  --output <filename>         - Custom output filename (saves to Downloads folder)")
        print("\n💡 Tips:")
        print("  • Reports are automatically saved to your Downloads folder")
        print("  • Use '--no-clone' for faster analysis of public repositories")
        print("  • Security reviews focus on vulnerabilities and best practices")
        print("  • Performance reviews analyze code efficiency and optimization")
    
    def parse_command(self, command: str):
        """Parse user command."""
        parts = command.strip().split()
        if not parts:
            return None, {}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "review":
            return self.parse_review_command(args)
        elif cmd == "help":
            return "help", {}
        elif cmd == "version":
            return "version", {}
        elif cmd == "exit":
            return "exit", {}
        else:
            return "unknown", {"command": cmd}
    
    def parse_review_command(self, args):
        """Parse review command arguments."""
        if not args:
            return "error", {"message": "Please provide a repository URL"}
        
        repo_url = args[0]
        options = {}
        
        # Parse additional options
        i = 1
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                options["review_type"] = args[i + 1]
                i += 2
            elif args[i] == "--format" and i + 1 < len(args):
                options["output_format"] = args[i + 1]
                i += 2
            elif args[i] == "--output" and i + 1 < len(args):
                options["output_file"] = args[i + 1]
                i += 2
            elif args[i] == "--no-clone":
                options["clone_locally"] = False
                i += 1
            else:
                i += 1
        
        return "review", {"repo_url": repo_url, **options}
    
    async def execute_review(self, repo_url: str, options: dict):
        """Execute the review command."""
        print(f"\n🔍 Starting code review for: {repo_url}")
        print("⏳ This may take a few minutes...")
        
        try:
            # Set default options
            review_type = options.get("review_type", "full")
            output_format = options.get("output_format", "summary")
            clone_locally = options.get("clone_locally", True)
            output_file = options.get("output_file")
            
            # Generate default output filename if not provided
            if not output_file:
                repo_name = repo_url.replace('https://github.com/', '').replace('/', '_')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"code_review_{repo_name}_{timestamp}.json"
                # This will be automatically saved to Downloads folder by the agent
            
            print(f"📊 Review type: {review_type}")
            print(f"📄 Output format: {output_format}")
            print(f"💾 Output file: {output_file}")
            print(f"📁 Clone locally: {clone_locally}")
            
            # Execute the review
            report = self.agent.review_repository(
                repo_url=repo_url,
                output_file=output_file,
                clone_locally=clone_locally
            )
            
            if report["success"]:
                print("\n✅ Code review completed successfully!")
                self.agent.print_report_summary(report)
                
                # Clean up local repository if it was cloned
                if report.get("local_path"):
                    self.agent.cleanup_local_repository(report["local_path"])
                    print("🧹 Local repository cleaned up")
                
                return True
            else:
                print(f"\n❌ Code review failed: {report.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during code review: {str(e)}")
            return False
    
    async def run(self):
        """Run the CLI."""
        self.print_banner()
        
        while True:
            try:
                command = input("\n🔍 Code Review > ").strip()
                
                if not command:
                    continue
                
                cmd, args = self.parse_command(command)
                
                if cmd == "help":
                    self.print_help()
                elif cmd == "version":
                    print(f"�� GitHub Code Review Agent CLI v{self.version}")
                elif cmd == "exit":
                    print("👋 Goodbye!")
                    break
                elif cmd == "review":
                    success = await self.execute_review(args["repo_url"], args)
                    if success:
                        print("\n🎉 Review completed! Check the Downloads folder for the detailed report.")
                elif cmd == "error":
                    print(f"❌ {args['message']}")
                elif cmd == "unknown":
                    print(f"❌ Unknown command: {args['command']}")
                    print("Type 'help' for available commands")
                else:
                    print("❌ Unexpected error")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GitHub Code Review Agent CLI")
    parser.add_argument("--repo", help="Repository URL to review")
    parser.add_argument("--type", default="full", choices=["full", "security", "performance", "style"], 
                       help="Review type")
    parser.add_argument("--format", default="summary", choices=["summary", "detailed", "json"], 
                       help="Output format")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--no-clone", action="store_true", help="Don't clone locally")
    
    args = parser.parse_args()
    
    if args.repo:
        # Single command mode
        agent = GitHubReviewAgent()
        options = {
            "review_type": args.type,
            "output_format": args.format,
            "clone_locally": not args.no_clone
        }
        if args.output:
            options["output_file"] = args.output
        
        async def run_single():
            cli = CodeReviewCLI()
            await cli.execute_review(args.repo, options)
        
        asyncio.run(run_single())
    else:
        # Interactive mode
        cli = CodeReviewCLI()
        asyncio.run(cli.run())

if __name__ == "__main__":
    main() 