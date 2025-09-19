import requests
import json

# Test the fixed Signup API
def test_signup():
    url = "http://127.0.0.1:5001/api/signup"
    
    # Test data
    user_data = {
        "name": "testuser123",
        "email": "testuser123@example.com"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(user_data), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Signup successful!")
            return True
        else:
            print("❌ Signup failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask app first.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login():
    url = "http://127.0.0.1:5001/api/login"
    
    login_data = {
        "name": "testuser123",
        "email": "testuser123@example.com"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(login_data), headers=headers)
        print(f"Login Status Code: {response.status_code}")
        print(f"Login Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed!")
            return False
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Signup API...")
    if test_signup():
        print("\n🧪 Testing Login API...")
        test_login()