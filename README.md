# Flask Kanban Board API

A simple Flask-based REST API for user management with web interface. This project serves as a foundation for a Kanban board application with user authentication.

## 🚀 Features

- **REST API** for user management (CRUD operations)
- **Web Interface** for user login
- **SQLite Database** for data persistence
- **Password Hashing** using Werkzeug security
- **Unit Testing** with pytest
- **Flask-RESTful** for clean API structure

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Web Routes](#web-routes)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd flask-based-kanban
   ```

2. **Create virtual environment**
   ```bash
   python -m venv myvenv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   myvenv\Scripts\activate
   
   # macOS/Linux
   source myvenv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python api.py
   ```

6. **Access the application**
   - Web Interface: http://127.0.0.1:5001
   - API Base URL: http://127.0.0.1:5001/api

## 🎯 Usage

### Web Interface

1. Navigate to `http://127.0.0.1:5001`
2. Enter your email and name (password)
3. If user doesn't exist, create one via API first
4. Login to access success page

### API Usage

Use tools like Postman, curl, or any HTTP client to interact with the API.

## 📡 API Endpoints

### Users Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/api/users/` | Get all users | - |
| `POST` | `/api/users/` | Create new user | `{"name": "username", "email": "user@email.com"}` |
| `GET` | `/api/users/<id>` | Get user by ID | - |
| `PATCH` | `/api/users/<id>` | Update user | `{"name": "newname", "email": "newemail@email.com"}` |
| `DELETE` | `/api/users/<id>` | Delete user | - |

### Authentication

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/api/login` | User login | `{"email": "user@email.com", "name": "password"}` |

### Example API Calls

**Create a new user:**
```bash
curl -X POST http://127.0.0.1:5001/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "john_doe", "email": "john@example.com"}'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "name": "john_doe"}'
```

**Get all users:**
```bash
curl -X GET http://127.0.0.1:5001/api/users/
```

## 🌐 Web Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET, POST | Home page with login form |
| `/success` | GET | Success page after login |
| `/unsuccess` | GET | Error page for failed login |

## 🧪 Testing

Run the test suite using pytest:

```bash
# Run all tests
pytest

# Run specific test
pytest api.py::test_users_api -v

# Run tests with coverage
pytest --cov=api

# Run tests in verbose mode
pytest -v
```

### Test Coverage

Current tests include:
- ✅ Users API endpoint functionality
- 🔄 More tests planned for complete coverage

## 📁 Project Structure

```
flask-based-kanban/
├── api.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
├── instance/             # Database storage
│   └── database.db       # SQLite database
├── templates/            # HTML templates
│   ├── index.html        # Login page
│   ├── success.html      # Success page
│   └── unsuccess.html    # Error page
├── static/              # Static files (CSS, JS, images)
└── myvenv/              # Virtual environment (not in git)
```

## 🔧 Technologies Used

- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-RESTful** - REST API framework
- **SQLite** - Database
- **Werkzeug** - Password hashing
- **pytest** - Testing framework
- **HTML/CSS** - Frontend templates

## ⚙️ Configuration

### Database

The application uses SQLite database stored in `instance/database.db`. The database is automatically created on first run.

### Security

- Passwords are hashed using Werkzeug's `generate_password_hash`
- Secret key is used for session management (change in production!)

### Environment Variables

For production, consider setting:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
```

## 🚧 Development Roadmap

- [ ] Add task management (Kanban cards)
- [ ] Add board creation and management
- [ ] Implement JWT authentication
- [ ] Add user roles and permissions
- [ ] Create React/Vue frontend
- [ ] Add Docker support
- [ ] Implement file uploads
- [ ] Add email notifications

## 🐛 Known Issues

- Delete method in User class has incorrect indentation
- No input validation on frontend
- Basic error handling needs improvement

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

- **Your Name** - [Your GitHub Profile](https://github.com/yourusername)

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Python community for amazing libraries

---

**Note:** This is a development version. For production use, please implement proper security measures, environment variables, and error handling.
