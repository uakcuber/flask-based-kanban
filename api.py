from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, abort, Resource, reqparse, fields, marshal_with
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from sqlalchemy.exc import IntegrityError
import os
import pytest

app = Flask(__name__)
app.secret_key = 'benimgizlianahtarim123'  # Flash mesajları için - istediğin herhangi bir text

# Basit Flask uygulaması

api = Api(app)

# Use absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "instance", "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Create tables within application context
with app.app_context():
    if not os.path.exists(os.path.join(basedir, "instance")):
        os.makedirs(os.path.join(basedir, "instance"))
    db.create_all()
    print("Database tables created successfully!")

# Flask Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    if "UNIQUE constraint" in str(error):
        return jsonify({"error": "User with this name or email already exists"}), 400
    return jsonify({"error": "Database constraint violation"}), 400


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)  # name hem username hem password
    email = db.Column(db.String, unique=True, nullable=False)
    name_hash = db.Column(db.String, nullable=False)  # name'i hash'li tut
    
    def set_name_as_password(self, name):
        """Name'i password olarak hash'leyerek kaydet"""
        self.name = name
        self.name_hash = generate_password_hash(name)
    
    def check_name_as_password(self, name):
        """Name'i password olarak kontrol et"""
        return check_password_hash(self.name_hash, name)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"


user_args = reqparse.RequestParser()
user_args.add_argument("name", type=str, help="Name cannot be blank", required=True)
user_args.add_argument("email", type=str, help="Email cannot be blank", required=True)

userfields = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String
}



class Users(Resource):
    @marshal_with(userfields)
    def get(self):
        """Kullanıcı listesi"""
        users = UserModel.query.all()
        if not users:
            abort(404, message="No users found")
        return users

    @marshal_with(userfields)
    def post(self):
        """Yeni kullanıcı kaydı (public)"""
        args = user_args.parse_args()
        user = UserModel(email=args["email"])
        user.set_name_as_password(args["name"])  # Name'i hem username hem password olarak ayarla
        db.session.add(user)
        db.session.commit()
        return user, 201
    

class User(Resource):
    @marshal_with(userfields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user
        
    @marshal_with(userfields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        if args["name"]:
            user.set_name_as_password(args["name"])  # Update name and hash
        if args["email"]:
            user.email = args["email"]
        db.session.commit()
        return user
        
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        return '', 204
                


# API Login endpoint
class Login(Resource):
    def post(self):
        """API Login - basit login"""
        data = request.get_json()
        if not data or not data.get('email') or not data.get('name'):
            abort(400, message='Email and name required')
        
        user = UserModel.query.filter_by(email=data['email']).first()
        
        if user and user.check_name_as_password(data['name']):
            return {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }, 200
        else:
            abort(401, message='Invalid credentials')


# Fixed Signup class
class Signup(Resource):
    @marshal_with(userfields)
    def post(self):
        """Create new user via JSON - proper signup"""
        data = request.get_json()
        
        if not data:
            abort(400, message="JSON data required")
            
        if not data.get("name") or not data.get("email"):
            abort(400, message="Name and email are required")
        
        # Create new user
        user = UserModel(email=data["email"])
        user.set_name_as_password(data["name"])
        
        db.session.add(user)
        db.session.commit()
        
        return user, 201


api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/users/<int:id>")
api.add_resource(Login, "/api/login")
api.add_resource(Signup, "/api/signup")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print("🔍 DEBUG: Form submitted")
        email = request.form.get("email")
        name = request.form.get("password")  # HTML'de password field ama aslında name alıyoruz
        
        print(f"🔍 DEBUG: email='{email}', name='{name}'")
        
        if not email or not name:
            print("❌ DEBUG: Missing fields")
            flash("Please fill in all fields.")
            return redirect(url_for("unsuccess"))
        
        user = UserModel.query.filter_by(email=email).first()
        print(f"🔍 DEBUG: User found: {user}")
        
        # Name'i password olarak kontrol et
        if user and user.check_name_as_password(name):
            print("✅ DEBUG: Login successful")
            flash(f"Welcome {user.name}!")
            return redirect(url_for("success"))
        else:
            print("❌ DEBUG: Invalid credentials")
            flash("Invalid email or name. Please try again.")
            return redirect(url_for("unsuccess"))

    return render_template('index.html')

@app.route("/success")
def success():
    return render_template('success.html')

@app.route("/unsuccess")
def unsuccess():
    return render_template('unsuccess.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print("🔍 DEBUG: Register form submitted")
        name = request.form.get("name")
        email = request.form.get("email")
        
        print(f"🔍 DEBUG: name='{name}', email='{email}'")
        
        if not name or not email:
            print("❌ DEBUG: Missing fields")
            flash("Please fill in all fields.")
            return redirect(url_for("unsuccess"))
        
        # Check if user already exists
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            print("❌ DEBUG: User already exists")
            flash("A user with this email already exists.")
            return redirect(url_for("unsuccess"))
        
        # Create new user
        user = UserModel(email=email)
        user.set_name_as_password(name)
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ DEBUG: User registered successfully")
        flash(f"Registration successful! Welcome {user.name}! You can now login.")
        return redirect(url_for("success"))

    return render_template('register.html')



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_users_api(client):
    response = client.get('/api/users/')
    assert response.status_code in [200, 404]  # Either success or no users found



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)


