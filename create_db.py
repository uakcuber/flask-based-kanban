from api import app, db, UserModel

with app.app_context():
    # Create tables only if they don't exist
    db.create_all()
    print("Database tables created/verified successfully!")
    