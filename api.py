from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, abort, Resource, reqparse, fields, marshal_with
from werkzeug.security import generate_password_hash, check_password_hash
import os

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
    try:
        if not os.path.exists(os.path.join(basedir, "instance")):
            os.makedirs(os.path.join(basedir, "instance"))
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")


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

# JWT kısımları kaldırıldı - basit tutuyoruz

class Users(Resource):
    @marshal_with(userfields)
    def get(self):
        """Kullanıcı listesi"""
        try:
            users = UserModel.query.all()
            if not users:
                abort(404, message="No users found")
            return users
        except Exception as e:
            print(f"Database error: {e}")
            abort(500, message="Internal server error occurred")

    @marshal_with(userfields)
    def post(self):
        """Yeni kullanıcı kaydı (public)"""
        try:
            args = user_args.parse_args()
            user = UserModel(email=args["email"])
            user.set_name_as_password(args["name"])  # Name'i hem username hem password olarak ayarla
            db.session.add(user)
            db.session.commit()
            return user, 201
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
            if "UNIQUE constraint" in str(e):
                abort(400, message="User with this name or email already exists")
            abort(500, message="Internal server error occurred")
    

class User(Resource):
    @marshal_with(userfields)
    def get(self, id):
        try:
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                abort(404, message="User not found")
            return user
        except Exception as e:
            print(f"Database error: {e}")
            abort(500, message="Internal server error occurred")
        
    @marshal_with(userfields)
    def patch(self, id):
        try:
            args = user_args.parse_args()
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                abort(404, message="User not found")
            if args["name"]:
                user.name = args["name"]
            if args["email"]:
                user.email = args["email"]
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
            if "UNIQUE constraint" in str(e):
                abort(400, message="User with this name or email already exists")
            abort(500, message="Internal server error occurred")
        
        def delete(self, id):
            try:
                user = UserModel.query.filter_by(id=id).first()
                if not user:
                    abort(404, message="User not found")
                db.session.delete(user)
                db.session.commit()
                return '', 204
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {e}")
                abort(500, message="Internal server error occurred")
                


# API Login endpoint
class Login(Resource):
    def post(self):
        """API Login - basit login"""
        try:
            data = request.get_json()
            if not data or not data.get('email') or not data.get('name'):
                return {'message': 'Email and name required'}, 400
            
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
                return {'message': 'Invalid credentials'}, 401
                
        except Exception as e:
            print(f"Login error: {e}")
            return {'message': 'Internal server error'}, 500

api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/users/<int:id>")
api.add_resource(Login, "/api/login")


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
        
        try:
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
        except Exception as e:
            print(f"💥 DEBUG: Database error: {e}")
            flash("Database error occurred.")
            return redirect(url_for("unsuccess"))

    return render_template('index.html')

@app.route("/success")
def success():
    return render_template('success.html')

@app.route("/unsuccess")
def unsuccess():
    return render_template('unsuccess.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)


