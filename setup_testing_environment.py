#!/usr/bin/env python3
"""
Setup script for testing environment
Helps configure everything needed to test all code on all branches
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class TestingEnvironmentSetup:
    """Setup testing environment"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_result(self, step: str, success: bool, details: str = ""):
        """Print setup result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} {step}")
        if details:
            print(f"   └─ {details}")
        
        if not success:
            self.issues_found.append({
                "step": step,
                "details": details
            })
        else:
            self.fixes_applied.append({
                "step": step,
                "details": details
            })
    
    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_result("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.print_result("Python Version", False, f"Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
            return False
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        self.print_header("Installing Dependencies")
        
        try:
            # Check if requirements.txt exists
            if not os.path.exists("requirements.txt"):
                self.print_result("Requirements File", False, "requirements.txt not found")
                return False
            
            # Install dependencies
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.print_result("Dependencies Installation", True, "All packages installed successfully")
                return True
            else:
                self.print_result("Dependencies Installation", False, f"Installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_result("Dependencies Installation", False, "Installation timed out")
            return False
        except Exception as e:
            self.print_result("Dependencies Installation", False, f"Exception: {e}")
            return False
    
    def setup_environment_variables(self) -> bool:
        """Setup environment variables"""
        self.print_header("Setting Up Environment Variables")
        
        # Check current environment
        required_vars = {
            "GITHUB_TOKEN": "GitHub personal access token",
            "GMAIL_USER": "Gmail username",
            "GMAIL_APP_PASSWORD": "Gmail app password"
        }
        
        missing_vars = []
        for var_name, description in required_vars.items():
            if not os.getenv(var_name):
                missing_vars.append((var_name, description))
        
        if not missing_vars:
            self.print_result("Environment Variables", True, "All required variables are set")
            return True
        
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            env_file.touch()
        
        # Add missing variables to .env file
        with open(env_file, "a") as f:
            for var_name, description in missing_vars:
                f.write(f"\n# {description}\n")
                f.write(f"# {var_name}=your-value-here\n")
        
        self.print_result("Environment Variables", False, f"Missing variables: {[var for var, _ in missing_vars]}")
        print("   📝 Added template to .env file")
        print("   💡 Please set the following environment variables:")
        for var_name, description in missing_vars:
            print(f"      {var_name}: {description}")
        
        return False
    
    def setup_git_config(self) -> bool:
        """Setup git configuration"""
        self.print_header("Setting Up Git Configuration")
        
        try:
            # Check git configuration
            result = subprocess.run(
                ["git", "config", "--get", "user.name"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.print_result("Git User Name", True, result.stdout.strip())
            else:
                self.print_result("Git User Name", False, "Not configured")
                print("   💡 Run: git config --global user.name 'Your Name'")
            
            result = subprocess.run(
                ["git", "config", "--get", "user.email"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.print_result("Git User Email", True, result.stdout.strip())
            else:
                self.print_result("Git User Email", False, "Not configured")
                print("   💡 Run: git config --global user.email 'your-email@example.com'")
            
            return True
            
        except Exception as e:
            self.print_result("Git Configuration", False, f"Exception: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Setup database files"""
        self.print_header("Setting Up Database")
        
        try:
            # Check if database files exist
            db_files = ["alerts.db", "messages.db"]
            created_files = []
            
            for db_file in db_files:
                if not os.path.exists(db_file):
                    # Create empty database
                    import sqlite3
                    conn = sqlite3.connect(db_file)
                    conn.close()
                    created_files.append(db_file)
            
            if created_files:
                self.print_result("Database Setup", True, f"Created: {', '.join(created_files)}")
            else:
                self.print_result("Database Setup", True, "All database files exist")
            
            return True
            
        except Exception as e:
            self.print_result("Database Setup", False, f"Exception: {e}")
            return False
    
    def create_test_scripts(self) -> bool:
        """Create missing test scripts"""
        self.print_header("Creating Test Scripts")
        
        # Check if comprehensive test script exists
        if not os.path.exists("test_all_branches_comprehensive.py"):
            self.print_result("Comprehensive Test Script", False, "test_all_branches_comprehensive.py not found")
            print("   💡 Run the comprehensive testing script I created earlier")
        else:
            self.print_result("Comprehensive Test Script", True, "Script exists")
        
        # Check if diagnostic script exists
        if not os.path.exists("diagnose_email_body_issue.py"):
            self.print_result("Email Diagnostic Script", False, "diagnose_email_body_issue.py not found")
            print("   💡 Run the email diagnostic script I created earlier")
        else:
            self.print_result("Email Diagnostic Script", True, "Script exists")
        
        return True
    
    def setup_mcp_server(self) -> bool:
        """Setup MCP server"""
        self.print_header("Setting Up MCP Server")
        
        # Check if MCP server files exist
        mcp_files = [
            "simple_mcp_server.py",
            "github_mcp_bridge.py",
            "simple_mcp_http_server.py"
        ]
        
        existing_files = []
        for mcp_file in mcp_files:
            if os.path.exists(mcp_file):
                existing_files.append(mcp_file)
        
        if existing_files:
            self.print_result("MCP Server Files", True, f"Found: {', '.join(existing_files)}")
            print("   💡 Start MCP server with: python simple_mcp_server.py")
        else:
            self.print_result("MCP Server Files", False, "No MCP server files found")
        
        return len(existing_files) > 0
    
    def create_testing_guide(self) -> bool:
        """Create testing guide"""
        self.print_header("Creating Testing Guide")
        
        guide_content = """# 🧪 Testing Guide for All Branches

## Quick Start

1. **Setup Environment**:
   ```bash
   python setup_testing_environment.py
   ```

2. **Start MCP Server**:
   ```bash
   python simple_mcp_server.py &
   ```

3. **Run Comprehensive Tests**:
   ```bash
   python test_all_branches_comprehensive.py
   ```

4. **Diagnose Email Issues**:
   ```bash
   python diagnose_email_body_issue.py
   ```

## Environment Variables

Set these in your shell or .env file:
```bash
export GITHUB_TOKEN="your-github-token"
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
```

## Common Issues

### MCP Server Not Running
- Start with: `python simple_mcp_server.py`
- Check port 5000 is available
- Verify server responds to health checks

### Email Body Issues
- Run: `python diagnose_email_body_issue.py`
- Check Gmail credentials
- Verify sendmail configuration

### Git Issues
- Configure git user: `git config --global user.name "Your Name"`
- Configure git email: `git config --global user.email "your-email@example.com"`

## Test Results

- Comprehensive results: `comprehensive_test_results.json`
- Test logs: `test_results.log`
- Coverage reports: `htmlcov/`

## Branch Testing

The comprehensive test script will:
1. Check all branches
2. Test each branch with commits
3. Run pytest with coverage
4. Run integration tests
5. Test branch-specific functionality
6. Generate detailed reports

## Troubleshooting

If tests fail:
1. Check prerequisites with diagnostic scripts
2. Verify environment variables
3. Ensure MCP server is running
4. Check git configuration
5. Review test logs for specific errors
"""
        
        try:
            with open("TESTING_GUIDE.md", "w") as f:
                f.write(guide_content)
            
            self.print_result("Testing Guide", True, "Created TESTING_GUIDE.md")
            return True
            
        except Exception as e:
            self.print_result("Testing Guide", False, f"Exception: {e}")
            return False
    
    def run_setup(self):
        """Run complete setup"""
        print("🚀 Setting Up Testing Environment")
        print("⏰ This will configure everything needed for comprehensive testing")
        
        # Run all setup steps
        steps = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.install_dependencies),
            ("Environment Variables", self.setup_environment_variables),
            ("Git Configuration", self.setup_git_config),
            ("Database Setup", self.setup_database),
            ("Test Scripts", self.create_test_scripts),
            ("MCP Server", self.setup_mcp_server),
            ("Testing Guide", self.create_testing_guide),
        ]
        
        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                self.print_result(step_name, False, f"Exception: {e}")
        
        # Summary
        self.print_header("Setup Summary")
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        print(f"❌ Issues Found: {len(self.issues_found)}")
        
        if self.issues_found:
            print("\n🔧 Issues that need manual attention:")
            for issue in self.issues_found:
                print(f"   • {issue['step']}: {issue['details']}")
        
        print("\n🎯 Next Steps:")
        print("   1. Set environment variables (see .env file)")
        print("   2. Start MCP server: python simple_mcp_server.py")
        print("   3. Run comprehensive tests: python test_all_branches_comprehensive.py")
        print("   4. Check TESTING_GUIDE.md for detailed instructions")
        
        return len(self.issues_found) == 0

def main():
    """Main function"""
    setup = TestingEnvironmentSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup complete! Ready for testing.")
        sys.exit(0)
    else:
        print("\n⚠️  Setup completed with issues. Please address them before testing.")
        sys.exit(1)

if __name__ == "__main__":
    main() 