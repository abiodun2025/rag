#!/usr/bin/env python3
"""
Interactive Call - Input number when prompted
"""

import subprocess
import sys

def get_phone_number():
    """Get phone number from user input."""
    print("📞 Terminal Call Agent")
    print("=" * 30)
    
    while True:
        number = input("Enter phone number to call: ").strip()
        
        if number:
            # Clean up the number
            number = number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            # Add +1 if it's a US number without country code
            if len(number) == 10 and number.isdigit():
                number = '+1' + number
            elif not number.startswith('+'):
                number = '+' + number
            
            return number
        else:
            print("❌ Please enter a valid phone number")

def make_call(phone_number: str):
    """Make a call to the given number."""
    print(f"\n📞 Making call to {phone_number}...")
    
    try:
        # Use macOS system dialer
        subprocess.run(['open', f'tel:{phone_number}'], check=True)
        print("✅ Call initiated successfully!")
        print("📞 Check your phone/system for the call")
        return True
    except Exception as e:
        print(f"❌ Call failed: {e}")
        print("📞 Try manually dialing the number")
        return False

def main():
    """Main interactive function."""
    try:
        while True:
            # Get phone number
            phone_number = get_phone_number()
            
            # Make the call
            success = make_call(phone_number)
            
            # Ask if user wants to make another call
            if success:
                again = input("\n📞 Make another call? (y/n): ").strip().lower()
                if again not in ['y', 'yes']:
                    print("👋 Goodbye!")
                    break
            else:
                again = input("\n📞 Try again? (y/n): ").strip().lower()
                if again not in ['y', 'yes']:
                    print("👋 Goodbye!")
                    break
            
            print("\n" + "=" * 30)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 