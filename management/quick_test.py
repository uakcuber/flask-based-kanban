#!/usr/bin/env python3
"""
Quick test for the API without external dependencies
Run from project root: python management/quick_test.py
"""

import urllib.request
import urllib.parse
import json
import sys
import os

# Add parent directory to path to import from api.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_signup_simple():
    """Test signup using only built-in libraries"""
    url = "http://127.0.0.1:5001/api/signup"
    
    # Test data
    data = {
        "name": "testuser456",
        "email": "testuser456@example.com"
    }
    
    # Convert to JSON and encode
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url, 
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_data = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ Signup Status: {status_code}")
            print(f"✅ Response: {response_data}")
            
            if status_code == 201:
                print("🎉 Signup successful! User created in database.")
                return True
            else:
                print("❌ Unexpected status code")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure Flask server is running on http://127.0.0.1:5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_users_list():
    """Test getting users list"""
    url = "http://127.0.0.1:5001/api/users/"
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            response_data = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ Users List Status: {status_code}")
            print(f"✅ Users: {response_data}")
            return True
            
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Signup API (Simple Version)...")
    print("=" * 50)
    
    if test_signup_simple():
        print("\n🧪 Testing Users List...")
        test_users_list()
    
    print("\n" + "=" * 50)
    print("Test completed!")