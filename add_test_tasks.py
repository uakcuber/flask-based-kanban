import requests
import json

# Login first
login_data = {'email': 'test@example.com', 'name': 'testuser'}
session = requests.Session()
login_response = session.post('http://127.0.0.1:5001/api/login', json=login_data)
print('Login:', login_response.status_code)

# Get lists
lists_response = session.get('http://127.0.0.1:5001/api/boards/1')
if lists_response.status_code == 200:
    board = lists_response.json()
    lists = board.get('lists', [])
    
    # Add test tasks to different lists
    test_tasks = [
        {'title': 'Design user interface', 'description': 'Create mockups and wireframes', 'priority': 'high', 'list_id': lists[0]['id']},
        {'title': 'Set up database', 'description': 'Configure PostgreSQL and migrations', 'priority': 'medium', 'list_id': lists[1]['id']},
        {'title': 'Implement authentication', 'description': 'Add login and registration', 'priority': 'high', 'list_id': lists[1]['id']},
        {'title': 'Code review', 'description': 'Review pull request #123', 'priority': 'low', 'list_id': lists[2]['id']},
        {'title': 'Deploy to staging', 'description': 'Test in staging environment', 'priority': 'medium', 'list_id': lists[3]['id']},
    ]
    
    for task in test_tasks:
        response = session.post('http://127.0.0.1:5001/api/tasks/', json=task)
        if response.status_code == 201:
            print('✅ Created task:', task['title'])
        else:
            print('❌ Failed to create task:', task['title'], '-', response.status_code)
else:
    print('Failed to get board data')