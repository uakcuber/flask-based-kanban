import pytest
import json
import os
import tempfile
from api import app, db, UserModel

@pytest.fixture
def client():
    """Test client fixture"""
    # Create a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'name': 'testuser',
        'email': 'test@example.com'
    }

class TestUsersAPI:
    """Test cases for Users API endpoints"""
    
    def test_get_users_empty(self, client):
        """Test getting users when database is empty"""
        response = client.get('/api/users/')
        assert response.status_code in [200, 404]
    
    def test_create_user_success(self, client, sample_user_data):
        """Test successful user creation"""
        response = client.post('/api/users/', 
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        assert response.status_code == 201
        
        # Verify user was created
        data = json.loads(response.data)
        assert data['name'] == sample_user_data['name']
        assert data['email'] == sample_user_data['email']
    
    def test_create_user_duplicate_email(self, client, sample_user_data):
        """Test creating user with duplicate email"""
        # Create first user
        client.post('/api/users/', 
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Try to create duplicate
        duplicate_data = {
            'name': 'differentuser',
            'email': sample_user_data['email']  # Same email
        }
        response = client.post('/api/users/', 
                             data=json.dumps(duplicate_data),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_create_user_missing_data(self, client):
        """Test creating user with missing required fields"""
        incomplete_data = {'name': 'testuser'}  # Missing email
        response = client.post('/api/users/', 
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        assert response.status_code == 400

class TestUserAPI:
    """Test cases for individual User API endpoints"""
    
    def test_get_user_by_id(self, client, sample_user_data):
        """Test getting user by ID"""
        # Create user first
        create_response = client.post('/api/users/', 
                                    data=json.dumps(sample_user_data),
                                    content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Get user by ID
        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['name'] == sample_user_data['name']
    
    def test_get_nonexistent_user(self, client):
        """Test getting non-existent user"""
        response = client.get('/api/users/999')
        assert response.status_code == 404

class TestLoginAPI:
    """Test cases for Login API"""
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login"""
        # Create user first
        client.post('/api/users/', 
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Try to login
        login_data = {
            'email': sample_user_data['email'],
            'name': sample_user_data['name']  # name is used as password
        }
        response = client.post('/api/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials"""
        # Create user first
        client.post('/api/users/', 
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Try to login with wrong password
        login_data = {
            'email': sample_user_data['email'],
            'name': 'wrongpassword'
        }
        response = client.post('/api/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        assert response.status_code == 401
    
    def test_login_missing_data(self, client):
        """Test login with missing data"""
        incomplete_data = {'email': 'test@example.com'}  # Missing name
        response = client.post('/api/login',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        assert response.status_code == 400

class TestWebRoutes:
    """Test cases for web routes"""
    
    def test_home_page_get(self, client):
        """Test home page GET request"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data  # Basic HTML check
    
    def test_success_page(self, client):
        """Test success page"""
        response = client.get('/success')
        assert response.status_code == 200
    
    def test_unsuccess_page(self, client):
        """Test unsuccess page"""
        response = client.get('/unsuccess')
        assert response.status_code == 200