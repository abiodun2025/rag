#!/usr/bin/env python3
"""
Simple Dial - Just input number and dial
"""

import sys
import subprocess

def dial_number(phone_number: str):
    """Dial a number using system dialer."""
    print(f"📞 Dialing {phone_number}...")
    
    try:
        # Use macOS system dialer
        subprocess.run(['open', f'tel:{phone_number}'], check=True)
        print("✅ Call initiated!")
        print("📞 Check your phone/system")
        return True
    except:
        print("❌ System dialer failed")
        print("📞 Try manually dialing the number")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dial.py <number>")
        print("Example: python dial.py 4782313954")
        sys.exit(1)
    
    number = sys.argv[1]
    dial_number(number) 