# Flask Kanban Board API

A comprehensive Flask-based REST API for user management with modern web interface. This project features HTTPS security, Nginx proxy integration, and an interactive terminal-style homepage. Built as a foundation for a full-featured Kanban board application with robust user authentication.

## 🚀 Features

- **REST API** for user management (CRUD operations)
- **HTTPS Security** with SSL/TLS certificate generation
- **Nginx Proxy** integration for production-ready deployment
- **Interactive Homepage** with terminal-style UI and dynamic sizing
- **Modern Web Interface** for user login (UI design adapted from Bedimcode)
- **SQLite Database** for data persistence
- **Password Hashing** using Werkzeug security
- **Database Management Tools** (create, reset, check database)
- **Test User Creation** utility
- **Responsive Design** with SCSS styling
- **Unit Testing** with pytest
- **Flask-RESTful** for clean API structure

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Web Routes](#-web-routes)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Configuration](#-configuration)
- [Utilities](#-utilities)
- [Development Roadmap](#-development-roadmap)
- [Known Issues](#-known-issues)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)
- [Acknowledgments](#-acknowledgments)

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

5. **Initialize the database** (optional)
   ```bash
   python create_db.py
   ```

6. **Create SSL certificates** (for HTTPS)
   ```bash
   python create_ssl.py
   ```

7. **Run the application**
   ```bash
   python api.py
   ```

8. **Access the application**
   - **HTTPS (Recommended)**: https://localhost
   - **HTTP Fallback**: http://127.0.0.1:5000
   - **API Base URL**: https://localhost/api

## 🎯 Usage

### Web Interface

1. Navigate to `https://localhost` (HTTPS) or `http://127.0.0.1:5000` (HTTP)
2. Experience the interactive terminal-style homepage
3. Use the login interface with your email and name (password)
4. If user doesn't exist, create one via API first or use the test user creation utility
5. Login to access the success page

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
curl -k -X POST https://localhost/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "john_doe", "email": "john@example.com"}'
```

**Login:**
```bash
curl -k -X POST https://localhost/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "name": "john_doe"}'
```

**Get all users:**
```bash
curl -k -X GET https://localhost/api/users/
```

**Note:** The `-k` flag is used to bypass SSL certificate verification for self-signed certificates in development.

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
├── create_db.py           # Database initialization script
├── create_ssl.py          # SSL certificate generation
├── create_test_user.py    # Test user creation utility
├── check_db.py            # Database verification tool
├── reset_db.py            # Database reset utility
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── instance/             # Database storage
│   └── database.db       # SQLite database
├── templates/            # HTML templates
│   ├── homepage.html     # Interactive terminal homepage
│   ├── index.html        # Login page
│   ├── success.html      # Success page
│   └── unsuccess.html    # Error page
├── static/              # Static assets
│   ├── css/             # Compiled CSS
│   ├── scss/            # SCSS source files
│   └── img/             # Images and graphics
└── myvenv/              # Virtual environment (not in git)
```

## 🔧 Technologies Used

- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-RESTful** - REST API framework
- **Nginx** - Reverse proxy server
- **OpenSSL** - SSL/TLS certificate generation
- **SQLite** - Database
- **Werkzeug** - Password hashing and security
- **SCSS/Sass** - CSS preprocessing
- **JavaScript** - Interactive terminal UI (Termynal.js)
- **pytest** - Testing framework
- **HTML/CSS** - Frontend templates and styling

## ⚙️ Configuration

### Database

The application uses SQLite database stored in `instance/database.db`. Use the provided utilities:
- `python create_db.py` - Initialize database tables
- `python check_db.py` - Verify database status
- `python reset_db.py` - Reset database to clean state
- `python create_test_user.py` - Create test user for development

### Security

- **HTTPS/TLS**: SSL certificates auto-generated with `create_ssl.py`
- **Nginx Proxy**: Production-ready reverse proxy configuration
- **Password Hashing**: Secure password storage using Werkzeug
- **Self-signed Certificates**: Development SSL certificates (replace in production)

### Environment Variables

For production deployment:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

## 🚧 Development Roadmap

### Completed ✅
- [x] HTTPS/SSL certificate generation
- [x] Nginx proxy integration
- [x] Interactive terminal homepage
- [x] Responsive SCSS styling
- [x] Database management utilities
- [x] Production-ready security setup

### Planned 📋
- [ ] Add task management (Kanban cards)
- [ ] Add board creation and management
- [ ] Implement JWT authentication
- [ ] Add user roles and permissions
- [ ] Create React/Vue frontend
- [ ] Add Docker support
- [ ] Implement file uploads
- [ ] Add email notifications
- [ ] Add drag-and-drop functionality
- [ ] Implement real-time updates (WebSocket)

## 🐛 Known Issues

- Self-signed SSL certificates trigger browser warnings (expected in development)
- Basic error handling needs improvement for production use
- Frontend input validation could be enhanced
- Terminal UI animation performance could be optimized for slower devices

## 🔧 Utilities

The project includes several utility scripts for easier development:

```bash
# Database Management
python create_db.py        # Initialize database tables
python check_db.py         # Check database status and contents
python reset_db.py         # Reset database to clean state

# User Management  
python create_test_user.py # Create a test user for development

# Security Setup
python create_ssl.py       # Generate SSL certificates for HTTPS
```

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
- **Login Page Design**: The login page UI design is inspired by and adapted from [Bedimcode](https://github.com/bedimcode) - credit to their beautiful CSS designs

---

**Note:** This is a development version. For production use, please implement proper security measures, environment variables, and error handling.
