# Management Scripts

This folder contains all management, testing, and utility scripts for the Flask Kanban project.

## 📁 Directory Structure

```
management/
├── README.md              # This documentation file
├── pytest.ini            # Pytest configuration
├── test_api.py           # Comprehensive API tests
├── test_signup.py        # Signup functionality tests
├── quick_test.py         # Quick API testing script
├── check_db.py           # Database inspection utility
├── create_db.py          # Database creation script
├── create_ssl.py         # SSL certificate generation
├── create_test_user.py   # Test user creation utility
└── reset_db.py           # Database reset utility
```

## 🧪 Testing Scripts

### `test_api.py`
- **Purpose**: Comprehensive unit tests for all API endpoints
- **Usage**: `python management/test_api.py` or `pytest management/test_api.py`
- **Features**: Tests Users, User, Login, and Signup endpoints with fixtures

### `test_signup.py`
- **Purpose**: Specific tests for signup functionality with requests library
- **Usage**: `python management/test_signup.py`
- **Features**: Tests user creation and login flow

### `quick_test.py`
- **Purpose**: Quick API testing without external dependencies
- **Usage**: `python management/quick_test.py`
- **Features**: Uses built-in urllib, tests signup and user listing

### `pytest.ini`
- **Purpose**: Pytest configuration and settings
- **Features**: Test paths, coverage settings, markers

## 🗄️ Database Management

### `create_db.py`
- **Purpose**: Initialize database and create tables
- **Usage**: `python management/create_db.py`
- **Features**: Creates SQLite database with proper schema

### `check_db.py`
- **Purpose**: Inspect database contents and structure
- **Usage**: `python management/check_db.py`
- **Features**: Shows tables, user count, sample data

### `reset_db.py`
- **Purpose**: Reset database to clean state
- **Usage**: `python management/reset_db.py`
- **Features**: Drops and recreates all tables

### `create_test_user.py`
- **Purpose**: Create sample users for testing
- **Usage**: `python management/create_test_user.py`
- **Features**: Adds predefined test users to database

## 🔒 Security & SSL

### `create_ssl.py`
- **Purpose**: Generate SSL certificates for HTTPS
- **Usage**: `python management/create_ssl.py`
- **Features**: Creates self-signed certificates for development

## 🚀 Usage Examples

### Run All Tests
```bash
# Run comprehensive tests
pytest management/test_api.py -v

# Run with coverage
pytest management/test_api.py --cov=. --cov-report=html
```

### Quick API Testing
```bash
# Make sure Flask server is running first
python api.py

# In another terminal, run quick test
python management/quick_test.py
```

### Database Management
```bash
# Reset database
python management/reset_db.py

# Create test users
python management/create_test_user.py

# Check database contents
python management/check_db.py
```

## 📋 Development Workflow

1. **Start Development**
   ```bash
   python management/reset_db.py      # Clean database
   python management/create_test_user.py  # Add test data
   python api.py                      # Start server
   ```

2. **Test Changes**
   ```bash
   python management/quick_test.py    # Quick functionality test
   pytest management/test_api.py      # Full test suite
   ```

3. **Database Inspection**
   ```bash
   python management/check_db.py      # Verify data
   ```

## 🔄 CI/CD Integration

These scripts integrate with the GitHub Actions pipeline:

- `pytest.ini` - Configures test execution
- `test_api.py` - Main test suite for CI
- Database scripts - Can be used for test data setup

## 📝 Adding New Scripts

When adding new management scripts:

1. Place them in the `management/` folder
2. Add documentation to this README
3. Follow the naming convention: `action_target.py`
4. Include proper error handling and help text
5. Add to `.gitignore` if they generate temporary files

## 🛠️ Script Dependencies

Most scripts require the main Flask app imports:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import app, db, UserModel
```

This ensures scripts can access the main application context and models.