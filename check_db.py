#!/usr/bin/env python3
"""
Database Status Check
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app, db, UserModel

def check_database():
    with app.app_context():
        try:
            users = UserModel.query.all()
            print(f"📊 Database Status:")
            print(f"  Total users: {len(users)}")
            
            for user in users:
                print(f"  - ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    Name: {user.name}")
                print(f"    Has hash: {'Yes' if user.name_hash else 'No'}")
                
            if not users:
                print("❌ No users found! Run reset_db.py")
            else:
                print("✅ Database OK")
                
        except Exception as e:
            print(f"💥 Database Error: {e}")

if __name__ == "__main__":
    check_database()