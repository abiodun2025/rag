#!/usr/bin/env python3
"""
Twilio Setup Helper Script
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with Twilio credentials template."""
    
    env_content = """# Twilio Credentials
# Get these from https://console.twilio.com/
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Instructions:
# 1. Go to https://console.twilio.com/
# 2. Sign up for a free account
# 3. Get your Account SID and Auth Token
# 4. Buy a phone number (~$1/month)
# 5. Replace the values above with your actual credentials
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up...")
        backup_file = Path('.env.backup')
        env_file.rename(backup_file)
        print(f"✅ Backed up to {backup_file}")
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Twilio credentials template")
    print("📝 Please edit .env with your actual Twilio credentials")

def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Run setup first.")
        return False
    
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    return True

def check_credentials():
    """Check if Twilio credentials are properly set."""
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing or invalid credentials: {', '.join(missing)}")
        return False
    
    print("✅ All Twilio credentials are set!")
    print(f"📞 Phone number: {os.getenv('TWILIO_PHONE_NUMBER')}")
    return True

def test_twilio_connection():
    """Test Twilio connection with current credentials."""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("❌ Missing Twilio credentials")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Test by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio connection successful!")
        print(f"   Account: {account.friendly_name}")
        print(f"   Status: {account.status}")
        return True
        
    except Exception as e:
        print(f"❌ Twilio connection failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Twilio Setup Helper")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            create_env_file()
            print("\n📋 Next steps:")
            print("1. Go to https://console.twilio.com/")
            print("2. Create a free account")
            print("3. Get your Account SID and Auth Token")
            print("4. Buy a phone number")
            print("5. Edit .env file with your credentials")
            print("6. Run: python setup_twilio.py test")
            
        elif command == "test":
            if load_env_file():
                if check_credentials():
                    test_twilio_connection()
            else:
                print("❌ Please run 'python setup_twilio.py init' first")
                
        elif command == "call":
            if load_env_file() and check_credentials():
                phone_number = input("Enter phone number to call (+1XXXXXXXXXX): ")
                if phone_number:
                    make_test_call(phone_number)
            else:
                print("❌ Please complete setup first")
        else:
            print("❌ Unknown command. Use: init, test, or call")
    else:
        print("Usage:")
        print("  python setup_twilio.py init  - Create .env template")
        print("  python setup_twilio.py test  - Test credentials")
        print("  python setup_twilio.py call  - Make test call")

def make_test_call(phone_number):
    """Make a test call using Twilio."""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        
        print(f"📞 Making test call to {phone_number}...")
        
        call = client.calls.create(
            to=phone_number,
            from_=from_number,
            twiml='<Response><Say>Hello! This is a test call from your MCP agent. The calling system is working perfectly!</Say></Response>'
        )
        
        print(f"✅ Call initiated!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   From: {from_number}")
        print(f"   To: {phone_number}")
        
    except Exception as e:
        print(f"❌ Call failed: {e}")

if __name__ == "__main__":
    main() 