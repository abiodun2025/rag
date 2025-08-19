#!/usr/bin/env python3
"""
GitHub App Setup Script
Helps configure GitHub App credentials for the code review agent.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

def setup_github_app():
    """Interactive setup for GitHub App credentials."""
    
    print("🤖 GitHub App Setup for Code Review Agent")
    print("=" * 50)
    print()
    print("This script will help you configure your GitHub App credentials.")
    print("Make sure you have created a GitHub App first!")
    print()
    print("📋 Prerequisites:")
    print("1. Create a GitHub App at: https://github.com/settings/apps")
    print("2. Get your App ID, Private Key, and Webhook Secret")
    print("3. Install the app on your repositories")
    print()
    
    # Load existing .env file
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv()
        print("📁 Found existing .env file")
    else:
        print("📁 Creating new .env file")
    
    print()
    
    # Get GitHub App ID
    print("🔢 Step 1: GitHub App ID")
    print("Enter your GitHub App ID (found on your app's page):")
    app_id = input("App ID: ").strip()
    
    if not app_id.isdigit():
        print("❌ Invalid App ID. Please enter a number.")
        return False
    
    # Get Private Key
    print()
    print("🔑 Step 2: Private Key")
    print("You can either:")
    print("1. Enter the private key content directly")
    print("2. Provide the path to your .pem file")
    print()
    
    key_choice = input("Choose option (1 or 2): ").strip()
    
    if key_choice == "1":
        print("Paste your private key content (including BEGIN and END lines):")
        print("Press Enter twice when done:")
        
        private_key_lines = []
        while True:
            line = input()
            if line.strip() == "" and private_key_lines and private_key_lines[-1].strip() == "":
                break
            private_key_lines.append(line)
        
        private_key = "\n".join(private_key_lines[:-1])  # Remove the last empty line
        
        if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            print("❌ Invalid private key format. Should start with '-----BEGIN RSA PRIVATE KEY-----'")
            return False
    
    elif key_choice == "2":
        print("Enter the path to your private key file:")
        key_path = input("Path: ").strip()
        
        if not os.path.exists(key_path):
            print(f"❌ File not found: {key_path}")
            return False
        
        try:
            with open(key_path, 'r') as f:
                private_key = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    
    else:
        print("❌ Invalid choice. Please select 1 or 2.")
        return False
    
    # Get Webhook Secret
    print()
    print("🔐 Step 3: Webhook Secret")
    print("Enter your webhook secret (from your GitHub App settings):")
    webhook_secret = input("Webhook Secret: ").strip()
    
    if len(webhook_secret) < 10:
        print("❌ Webhook secret should be at least 10 characters long.")
        return False
    
    # Get Cohere API Key
    print()
    print("🤖 Step 4: Cohere API Key")
    print("Enter your Cohere API key:")
    cohere_key = input("Cohere API Key: ").strip()
    
    if not cohere_key.startswith("sl"):
        print("❌ Invalid Cohere API key format. Should start with 'sl'")
        return False
    
    # Confirm settings
    print()
    print("📋 Configuration Summary:")
    print(f"App ID: {app_id}")
    print(f"Private Key: {'✓ Loaded' if private_key else '❌ Missing'}")
    print(f"Webhook Secret: {'✓ Set' if webhook_secret else '❌ Missing'}")
    print(f"Cohere API Key: {'✓ Set' if cohere_key else '❌ Missing'}")
    print()
    
    confirm = input("Save this configuration? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Configuration cancelled.")
        return False
    
    # Save to .env file
    env_content = f"""# GitHub App Configuration
GITHUB_APP_ID={app_id}
GITHUB_PRIVATE_KEY={private_key}
GITHUB_WEBHOOK_SECRET={webhook_secret}

# Cohere API Configuration
COHERE_API_KEY={cohere_key}

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Configuration saved to .env file!")
        print()
        
        # Test the configuration
        print("🧪 Testing configuration...")
        if test_configuration():
            print("✅ Configuration test passed!")
            print()
            print("🎉 Setup complete! You can now:")
            print("1. Run: python code_review_cli.py test-all")
            print("2. Start server: python code_review_cli.py server")
            print("3. Test manual review: python code_review_cli.py review")
            return True
        else:
            print("❌ Configuration test failed. Please check your settings.")
            return False
            
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False


def test_configuration():
    """Test the GitHub App configuration."""
    try:
        from app.config import settings
        
        # Test that all required settings are loaded
        required_settings = [
            'github_app_id',
            'github_private_key', 
            'github_webhook_secret',
            'cohere_api_key'
        ]
        
        for setting in required_settings:
            if not getattr(settings, setting, None):
                print(f"❌ Missing setting: {setting}")
                return False
        
        print("✅ All required settings are configured")
        
        # Test GitHub client initialization
        try:
            from app.github_client import GitHubClient
            client = GitHubClient()
            print("✅ GitHub client initialized")
        except Exception as e:
            print(f"❌ GitHub client test failed: {e}")
            return False
        
        # Test Cohere API
        try:
            import cohere
            co = cohere.Client(settings.cohere_api_key)
            print("✅ Cohere API client initialized")
        except Exception as e:
            print(f"❌ Cohere API test failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


def main():
    """Main function."""
    try:
        success = setup_github_app()
        if success:
            print("\n🚀 Your GitHub App is ready for the code review agent!")
        else:
            print("\n❌ Setup failed. Please check the guide and try again.")
            
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main() 