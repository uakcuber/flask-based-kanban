from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, abort, Resource, reqparse, fields, marshal_with
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from sqlalchemy.exc import IntegrityError
from functools import wraps
import os
import pytest
import subprocess

app = Flask(__name__)
app.secret_key = 'cokgizlikey'  # Flash mesajları için - istediğin herhangi bir text

# Basit Flask uygulaması

api = Api(app)

# Use absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "instance", "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Authentication helpers
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.endpoint.startswith('api.'):
                abort(401, message="Authentication required")
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return UserModel.query.get(session['user_id'])
    return None

def api_auth_required(f):
    """Decorator for API endpoints requiring authentication"""
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        if 'user_id' not in session:
            abort(401, message="Authentication required. Please login first.")
        
        # Add current user to the instance for easy access
        self.current_user = get_current_user()
        if not self.current_user:
            abort(401, message="Invalid session. Please login again.")
            
        return f(self, *args, **kwargs)
    return decorated_function

# Flask Error Handlers
@app.errorhandler(404)
def not_found(error):
    # API endpoint'leri için JSON response
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "API endpoint not found",
            "message": f"The endpoint '{request.path}' does not exist",
            "available_endpoints": [
                "/api/users/", "/api/login", "/api/signup",
                "/api/boards/", "/api/lists/", "/api/tasks/"
            ]
        }), 404
    
    # Web sayfaları için HTML template
    return render_template('404.html'), 404

@app.errorhandler(400)
def bad_request(error):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Bad request", "message": "Invalid request data"}), 400
    return render_template('404.html'), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Internal server error",
            "message": "Something went wrong on our end. Please try again later."
        }), 500
    return render_template('404.html'), 500

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
    
    # Relationships
    boards = db.relationship('BoardModel', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_name_as_password(self, name):
        """Name'i password olarak hash'leyerek kaydet"""
        self.name = name
        self.name_hash = generate_password_hash(name)
    
    def check_name_as_password(self, name):
        """Name'i password olarak kontrol et"""
        return check_password_hash(self.name_hash, name)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"


class BoardModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    
    # Relationships
    lists = db.relationship('ListModel', backref='board', lazy=True, cascade='all, delete-orphan', order_by='ListModel.position')
    
    def __repr__(self):
        return f"Board(title={self.title}, owner={self.owner.name})"


class ListModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    board_id = db.Column(db.Integer, db.ForeignKey('board_model.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('TaskModel', backref='list', lazy=True, cascade='all, delete-orphan', order_by='TaskModel.position')
    
    def __repr__(self):
        return f"List(title={self.title}, board={self.board.title})"


class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    list_id = db.Column(db.Integer, db.ForeignKey('list_model.id'), nullable=False)
    
    def __repr__(self):
        return f"Task(title={self.title}, list={self.list.title})"


user_args = reqparse.RequestParser()
user_args.add_argument("name", type=str, help="Name cannot be blank", required=True)
user_args.add_argument("email", type=str, help="Email cannot be blank", required=True)

board_args = reqparse.RequestParser()
board_args.add_argument("title", type=str, help="Title cannot be blank", required=True)
board_args.add_argument("description", type=str, required=False)
board_args.add_argument("user_id", type=int, help="User ID required", required=True)

list_args = reqparse.RequestParser()
list_args.add_argument("title", type=str, help="Title cannot be blank", required=True)
list_args.add_argument("position", type=int, required=False, default=0)
list_args.add_argument("board_id", type=int, help="Board ID required", required=True)

# Task args for POST (create)
task_create_args = reqparse.RequestParser()
task_create_args.add_argument("title", type=str, help="Title cannot be blank", required=True)
task_create_args.add_argument("description", type=str, required=False)
task_create_args.add_argument("position", type=int, required=False, default=0)
task_create_args.add_argument("priority", type=str, required=False, default='medium')
task_create_args.add_argument("list_id", type=int, help="List ID required", required=True)

# Task args for PATCH (update) - all optional
task_update_args = reqparse.RequestParser()
task_update_args.add_argument("title", type=str, required=False)
task_update_args.add_argument("description", type=str, required=False)
task_update_args.add_argument("position", type=int, required=False)
task_update_args.add_argument("priority", type=str, required=False)
task_update_args.add_argument("list_id", type=int, required=False)

userfields = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String
}

taskfields = {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "position": fields.Integer,
    "priority": fields.String,
    "created_at": fields.DateTime,
    "list_id": fields.Integer
}

listfields = {
    "id": fields.Integer,
    "title": fields.String,
    "position": fields.Integer,
    "board_id": fields.Integer,
    "tasks": fields.List(fields.Nested(taskfields))
}

boardfields = {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "created_at": fields.DateTime,
    "user_id": fields.Integer,
    "lists": fields.List(fields.Nested(listfields))
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

# Kanban API Resources
class Boards(Resource):
    @api_auth_required
    @marshal_with(boardfields)
    def get(self):
        """Get all boards for current user"""
        boards = BoardModel.query.filter_by(user_id=self.current_user.id).all()
        return boards
    
    @api_auth_required
    @marshal_with(boardfields)
    def post(self):
        """Create new board for current user"""
        args = board_args.parse_args()
        
        # Force user_id to current user (ignore any user_id from request)
        board = BoardModel(
            title=args["title"],
            description=args.get("description"),
            user_id=self.current_user.id
        )
        
        db.session.add(board)
        db.session.commit()
        return board, 201


class Board(Resource):
    @api_auth_required
    @marshal_with(boardfields)
    def get(self, id):
        """Get specific board with all lists and tasks (only if owned by current user)"""
        board = BoardModel.query.filter_by(id=id, user_id=self.current_user.id).first()
        if not board:
            abort(404, message="Board not found or access denied")
        return board
    
    @api_auth_required
    @marshal_with(boardfields)
    def patch(self, id):
        """Update board (only if owned by current user)"""
        board = BoardModel.query.filter_by(id=id, user_id=self.current_user.id).first()
        if not board:
            abort(404, message="Board not found or access denied")
            
        args = board_args.parse_args()
        if args.get("title"):
            board.title = args["title"]
        if args.get("description") is not None:
            board.description = args["description"]
            
        db.session.commit()
        return board
    
    @api_auth_required
    def delete(self, id):
        """Delete board (only if owned by current user)"""
        board = BoardModel.query.filter_by(id=id, user_id=self.current_user.id).first()
        if not board:
            abort(404, message="Board not found or access denied")
            
        db.session.delete(board)
        db.session.commit()
        return '', 204


class Lists(Resource):
    @api_auth_required
    @marshal_with(listfields)
    def post(self):
        """Create new list (only in user's own boards)"""
        args = list_args.parse_args()
        
        # Check if board exists and belongs to current user
        board = BoardModel.query.filter_by(id=args["board_id"], user_id=self.current_user.id).first()
        if not board:
            abort(404, message="Board not found or access denied")
        
        # Set position if not provided
        if not args.get("position"):
            max_position = db.session.query(db.func.max(ListModel.position)).filter_by(board_id=args["board_id"]).scalar()
            args["position"] = (max_position or 0) + 1
        
        list_item = ListModel(
            title=args["title"],
            position=args["position"],
            board_id=args["board_id"]
        )
        
        db.session.add(list_item)
        db.session.commit()
        return list_item, 201


class List(Resource):
    @api_auth_required
    @marshal_with(listfields)
    def patch(self, id):
        """Update list (only if in user's own board)"""
        list_item = ListModel.query.join(BoardModel).filter(
            ListModel.id == id,
            BoardModel.user_id == self.current_user.id
        ).first()
        if not list_item:
            abort(404, message="List not found or access denied")
            
        args = list_args.parse_args()
        if args.get("title"):
            list_item.title = args["title"]
        if args.get("position") is not None:
            list_item.position = args["position"]
            
        db.session.commit()
        return list_item
    
    @api_auth_required
    def delete(self, id):
        """Delete list (only if in user's own board and not protected)"""
        list_item = ListModel.query.join(BoardModel).filter(
            ListModel.id == id,
            BoardModel.user_id == self.current_user.id
        ).first()
        if not list_item:
            abort(404, message="List not found or access denied")
        
        # Protected lists that cannot be deleted
        PROTECTED_LISTS = ['Backlog', 'To Do', 'In Progress', 'Testing', 'Done']
        if list_item.title in PROTECTED_LISTS:
            abort(400, message=f"Cannot delete '{list_item.title}' - This is a protected system list")
            
        db.session.delete(list_item)
        db.session.commit()
        return '', 204


class Tasks(Resource):
    @api_auth_required
    @marshal_with(taskfields)
    def post(self):
        """Create new task (only in user's own lists)"""
        args = task_create_args.parse_args()
        
        # Check if list exists and belongs to current user's board
        list_item = ListModel.query.join(BoardModel).filter(
            ListModel.id == args["list_id"],
            BoardModel.user_id == self.current_user.id
        ).first()
        if not list_item:
            abort(404, message="List not found or access denied")
        
        # Set position if not provided
        if not args.get("position"):
            max_position = db.session.query(db.func.max(TaskModel.position)).filter_by(list_id=args["list_id"]).scalar()
            args["position"] = (max_position or 0) + 1
        
        task = TaskModel(
            title=args["title"],
            description=args.get("description"),
            position=args["position"],
            priority=args.get("priority", "medium"),
            list_id=args["list_id"]
        )
        
        db.session.add(task)
        db.session.commit()
        return task, 201


class Task(Resource):
    @api_auth_required
    @marshal_with(taskfields)
    def patch(self, id):
        """Update task (only if in user's own board)"""
        task = TaskModel.query.join(ListModel).join(BoardModel).filter(
            TaskModel.id == id,
            BoardModel.user_id == self.current_user.id
        ).first()
        if not task:
            abort(404, message="Task not found or access denied")
            
        args = task_update_args.parse_args()
        if args.get("title"):
            task.title = args["title"]
        if args.get("description") is not None:
            task.description = args["description"]
        if args.get("position") is not None:
            task.position = args["position"]
        if args.get("priority"):
            task.priority = args["priority"]
        if args.get("list_id"):
            # Verify new list also belongs to user before moving
            new_list = ListModel.query.join(BoardModel).filter(
                ListModel.id == args["list_id"],
                BoardModel.user_id == self.current_user.id
            ).first()
            if not new_list:
                abort(404, message="Target list not found or access denied")
            task.list_id = args["list_id"]
            
        db.session.commit()
        return task
    
    @api_auth_required
    def delete(self, id):
        """Delete task (only if in user's own board)"""
        task = TaskModel.query.join(ListModel).join(BoardModel).filter(
            TaskModel.id == id,
            BoardModel.user_id == self.current_user.id
        ).first()
        if not task:
            abort(404, message="Task not found or access denied")
            
        db.session.delete(task)
        db.session.commit()
        return '', 204


api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/users/<int:id>")
api.add_resource(Login, "/api/login")
api.add_resource(Signup, "/api/signup")

# Kanban API endpoints
api.add_resource(Boards, "/api/boards/")
api.add_resource(Board, "/api/boards/<int:id>")
api.add_resource(Lists, "/api/lists/")
api.add_resource(List, "/api/lists/<int:id>")
api.add_resource(Tasks, "/api/tasks/")
api.add_resource(Task, "/api/tasks/<int:id>")

@app.route("/")
def homepage():
    """Modern homepage with features and navigation"""
    return render_template("homepage.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        print("🔍 DEBUG: Form submitted")
        email = request.form.get("email")
        name = request.form.get("password")  # HTML'de password field ama aslında name alıyoruz
        
        print(f"🔍 DEBUG: email='{email}', name='{name}'")
        
        if not email or not name:
            print("❌ DEBUG: Missing fields")
            flash("⚠️ Missing Information: Please fill in both email and name fields.")
            return redirect(url_for("unsuccess"))
        
        user = UserModel.query.filter_by(email=email).first()
        print(f"🔍 DEBUG: User found: {user}")
        
        if not user:
            print("❌ DEBUG: User not found")
            flash(f"❌ Email Not Found: No account exists with email '{email}'. Please check your email or create a new account.")
            return redirect(url_for("unsuccess"))
        
        # Name'i password olarak kontrol et
        if user.check_name_as_password(name):
            print("✅ DEBUG: Login successful")
            # Set session data
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash(f"Welcome {user.name}!")
            return redirect(url_for("kanban"))  # Redirect to kanban instead of success
        else:
            print("❌ DEBUG: Wrong password")
            flash(f"🔑 Incorrect Name: The name you entered doesn't match our records for '{email}'. Please check your spelling and try again.")
            return redirect(url_for("unsuccess"))

    return render_template('login.html')

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
            if not name and not email:
                flash("⚠️ Missing Information: Please fill in both name and email fields.")
            elif not name:
                flash("⚠️ Missing Name: Please enter your name to complete registration.")
            else:
                flash("⚠️ Missing Email: Please enter your email address to complete registration.")
            return redirect(url_for("unsuccess"))
        
        # Validate email format
        if '@' not in email or '.' not in email:
            print("❌ DEBUG: Invalid email format")
            flash(f"📧 Invalid Email Format: '{email}' is not a valid email address. Please use format: example@domain.com")
            return redirect(url_for("unsuccess"))
        
        # Validate name length
        if len(name.strip()) < 2:
            print("❌ DEBUG: Name too short")
            flash("👤 Name Too Short: Your name must be at least 2 characters long.")
            return redirect(url_for("unsuccess"))
        
        # Check if user already exists by email
        existing_user_email = UserModel.query.filter_by(email=email).first()
        if existing_user_email:
            print("❌ DEBUG: Email already exists")
            flash(f"📧 Email Already Registered: An account with email '{email}' already exists. Please login instead or use a different email.")
            return redirect(url_for("unsuccess"))
        
        # Check if user already exists by name
        existing_user_name = UserModel.query.filter_by(name=name).first()
        if existing_user_name:
            print("❌ DEBUG: Name already exists")
            flash(f"👤 Username Taken: The name '{name}' is already registered. Please choose a different name.")
            return redirect(url_for("unsuccess"))
        
        # Create new user
        user = UserModel(email=email)
        user.set_name_as_password(name)
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ DEBUG: User registered successfully")
        # Auto-login after registration
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        flash(f"Registration successful! Welcome {user.name}!")
        return redirect(url_for("kanban"))

    return render_template('register.html')

@app.route("/kanban")
@login_required
def kanban():
    user = get_current_user()
    return render_template('kanban.html', user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for("homepage"))

@app.route("/test-404")
def test_404():
    """Test endpoint to demonstrate 404 page"""
    abort(404)



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_users_api(client):
    response = client.get('/api/users/')
    assert response.status_code in [200, 404]  # Either success or no users found



# Initialize database after all models are defined
with app.app_context():
    if not os.path.exists(os.path.join(basedir, "instance")):
        os.makedirs(os.path.join(basedir, "instance"))
    db.create_all()
    print("✅ Database tables created successfully!")

def start_nginx_if_available():
    """Simple nginx starter"""
    nginx_path = os.path.join(os.getcwd(), "nginx", "nginx.exe")
    if os.path.exists(nginx_path):
        try:
            # Check if already running
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq nginx.exe'], 
                                  capture_output=True, text=True)
            if 'nginx.exe' not in result.stdout:
                print("🚀 Starting Nginx HTTPS proxy...")
                subprocess.Popen([nginx_path], cwd=os.path.join(os.getcwd(), "nginx"))
                print("✅ Nginx started! Visit: https://localhost")
                return True
            else:
                print("✅ Nginx already running!")
                return True
        except:
            pass
    return False

if __name__ == '__main__':
    # Try to start nginx first
    nginx_started = start_nginx_if_available()
    
    if nginx_started:
        print("🔄 Running Flask behind Nginx proxy")
        print("🌐 Flask: http://127.0.0.1:5000")
        print("🔒 HTTPS: https://localhost")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("🔄 Running Flask directly")
        app.run(debug=True, host='127.0.0.1', port=5001)


