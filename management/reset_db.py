#!/usr/bin/env python3
"""
Database Reset Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app, db, UserModel

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Old tables dropped")
        
        # Create new tables
        db.create_all()
        print("New tables created")
        
        # Create test user
        test_user = UserModel(email="test@example.com")
        test_user.set_name_as_password("testuser")
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Database reset complete!")
        print("Test user created:")
        print("  Email: test@example.com")
        print("  Name/Password: testuser")

if __name__ == "__main__":
    reset_database()