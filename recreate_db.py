#!/usr/bin/env python3
"""
Database recreation script for Flask Kanban Board
This script will drop all existing tables and recreate them.
"""

import os
import sys

# Add the current directory to the Python path so we can import from api.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import app, db, UserModel, BoardModel, ListModel, TaskModel

def recreate_database():
    """Drop all tables and recreate them"""
    print("🔄 Recreating database tables...")
    
    with app.app_context():
        try:
            # Drop all existing tables
            print("❌ Dropping existing tables...")
            db.drop_all()
            
            # Create all tables fresh
            print("✅ Creating new tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {tables}")
            
            print("✅ Database recreation completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error recreating database: {str(e)}")
            return False

def create_test_user():
    """Create a test user for immediate testing"""
    print("\n👤 Creating test user...")
    
    with app.app_context():
        try:
            # Check if test user already exists
            existing_user = UserModel.query.filter_by(email='test@example.com').first()
            if existing_user:
                print("👤 Test user already exists")
                return existing_user
            
            # Create test user
            test_user = UserModel(
                name='testuser',
                email='test@example.com'
            )
            test_user.set_name_as_password('testuser')
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"✅ Test user created: {test_user.name} ({test_user.email})")
            return test_user
            
        except Exception as e:
            print(f"❌ Error creating test user: {str(e)}")
            db.session.rollback()
            return None

if __name__ == "__main__":
    print("🚀 Flask Kanban Database Recreation Tool")
    print("=" * 50)
    
    # Recreate database
    if recreate_database():
        # Create test user
        create_test_user()
        print("\n✅ Database setup completed!")
        print("You can now start the Flask application with: python api.py")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)