#!/bin/bash

# GitHub Token Setup Script
# This script helps you set up your GitHub token for the Code Review Agent

echo "🔑 GitHub Token Setup for Code Review Agent"
echo "============================================"
echo ""

# Check if token is already set
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN is already set in current session"
    echo "   Current token: ${GITHUB_TOKEN:0:10}..."
    echo ""
    read -p "Do you want to update it? (y/n): " update_choice
    if [[ $update_choice != "y" && $update_choice != "Y" ]]; then
        echo "👋 Keeping existing token. Exiting..."
        exit 0
    fi
fi

echo "📝 Please enter your GitHub token:"
echo "   (You can get one from: https://github.com/settings/tokens)"
echo "   (The token will be hidden as you type)"
echo ""
read -s -p "GitHub Token: " github_token
echo ""

if [ -z "$github_token" ]; then
    echo "❌ No token provided. Exiting..."
    exit 1
fi

echo ""
echo "🎯 Choose how to save your token:"
echo "1. Set for current session only (temporary)"
echo "2. Add to shell profile (~/.zshrc) for permanent access"
echo "3. Create .env file in project directory"
echo "4. All of the above"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "📝 Setting token for current session..."
        export GITHUB_TOKEN="$github_token"
        echo "✅ Token set for current session"
        ;;
    2)
        echo "📝 Adding token to ~/.zshrc..."
        # Remove existing GITHUB_TOKEN line if it exists
        sed -i '' '/export GITHUB_TOKEN=/d' ~/.zshrc
        # Add new token
        echo "export GITHUB_TOKEN=\"$github_token\"" >> ~/.zshrc
        echo "✅ Token added to ~/.zshrc"
        echo "🔄 Please run 'source ~/.zshrc' to load it in current session"
        ;;
    3)
        echo "📝 Creating .env file..."
        echo "GITHUB_TOKEN=$github_token" > .env
        echo "✅ Token saved to .env file"
        echo "🔄 Please run 'source .env' to load it in current session"
        ;;
    4)
        echo "📝 Setting up all options..."
        # Current session
        export GITHUB_TOKEN="$github_token"
        echo "✅ Token set for current session"
        
        # Shell profile
        sed -i '' '/export GITHUB_TOKEN=/d' ~/.zshrc
        echo "export GITHUB_TOKEN=\"$github_token\"" >> ~/.zshrc
        echo "✅ Token added to ~/.zshrc"
        
        # .env file
        echo "GITHUB_TOKEN=$github_token" > .env
        echo "✅ Token saved to .env file"
        ;;
    *)
        echo "❌ Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "🧪 Testing GitHub connection..."

# Test the connection
python3 -c "
import os
import requests

token = os.getenv('GITHUB_TOKEN')
if not token:
    print('❌ GITHUB_TOKEN not found in environment')
    exit(1)

headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
response = requests.get('https://api.github.com/user', headers=headers)

if response.status_code == 200:
    user_data = response.json()
    print(f'✅ Successfully connected to GitHub as: {user_data[\"login\"]}')
    print(f'📊 Public repos: {user_data.get(\"public_repos\", 0)}')
    print(f'🔒 Private repos: {user_data.get(\"total_private_repos\", 0)}')
else:
    print(f'❌ Connection failed: {response.status_code}')
    print(f'Error: {response.text}')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   • Run: python3 code_review_agent_cli.py test-connection"
echo "   • Run: python3 code_review_agent_cli.py list-prs"
echo "   • Run: python3 code_review_agent_cli.py select-pr"
echo ""
echo "🔒 Security reminder:"
echo "   • Never commit your token to version control"
echo "   • The .env file is already in .gitignore"
echo "   • Consider setting token expiration in GitHub settings" 