#!/usr/bin/env python3
"""
Test kullanıcısı oluştur
Email: test@example.com
Name/Password: testuser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app, db, UserModel

def create_test_user():
    with app.app_context():
        # Eski test kullanıcısını sil
        existing_user = UserModel.query.filter_by(email="test@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("Eski test kullanıcısı silindi")
        
        # Yeni test kullanıcısı oluştur
        test_user = UserModel(email="test@example.com")
        test_user.set_name_as_password("testuser")  # name = testuser, password da testuser
        
        db.session.add(test_user)
        db.session.commit()
        
        print("Test kullanıcısı oluşturuldu:")
        print(f"  Email: test@example.com")
        print(f"  Name/Password: testuser")
        print(f"  Login için bu bilgileri kullan!")

if __name__ == "__main__":
    create_test_user()