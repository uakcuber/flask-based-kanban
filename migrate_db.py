"""
Database migration script - preserves user data during conflicts
"""
from api import app, db, UserModel, BoardModel, ListModel, TaskModel
import json
import os
from datetime import datetime

def backup_database():
    """Backup all data to JSON"""
    with app.app_context():
        backup_data = {
            'users': [],
            'boards': [],
            'lists': [],
            'tasks': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Backup users
        for user in UserModel.query.all():
            backup_data['users'].append({
                'id': user.id,
                'name': user.name,
                'email': user.email
            })
        
        # Backup boards
        for board in BoardModel.query.all():
            backup_data['boards'].append({
                'id': board.id,
                'title': board.title,
                'description': board.description,
                'user_id': board.user_id,
                'created_at': board.created_at.isoformat() if board.created_at else None
            })
        
        # Backup lists
        for list_item in ListModel.query.all():
            backup_data['lists'].append({
                'id': list_item.id,
                'title': list_item.title,
                'position': list_item.position,
                'board_id': list_item.board_id,
                'created_at': list_item.created_at.isoformat() if list_item.created_at else None
            })
        
        # Backup tasks
        for task in TaskModel.query.all():
            backup_data['tasks'].append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'position': task.position,
                'priority': task.priority,
                'list_id': task.list_id,
                'created_at': task.created_at.isoformat() if task.created_at else None
            })
        
        # Save backup
        backup_file = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Database backup saved to: {backup_file}")
        return backup_file

def restore_database(backup_file):
    """Restore data from JSON backup"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return
    
    with app.app_context():
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        print(f"🔄 Restoring database from: {backup_file}")
        
        # Restore users
        for user_data in backup_data['users']:
            if not UserModel.query.get(user_data['id']):
                user = UserModel(
                    name=user_data['name'],
                    email=user_data['email']
                )
                user.id = user_data['id']
                db.session.add(user)
        
        # Restore boards
        for board_data in backup_data['boards']:
            if not BoardModel.query.get(board_data['id']):
                board = BoardModel(
                    title=board_data['title'],
                    description=board_data['description'],
                    user_id=board_data['user_id']
                )
                board.id = board_data['id']
                if board_data['created_at']:
                    board.created_at = datetime.fromisoformat(board_data['created_at'])
                db.session.add(board)
        
        # Restore lists
        for list_data in backup_data['lists']:
            if not ListModel.query.get(list_data['id']):
                list_item = ListModel(
                    title=list_data['title'],
                    position=list_data['position'],
                    board_id=list_data['board_id']
                )
                list_item.id = list_data['id']
                if list_data['created_at']:
                    list_item.created_at = datetime.fromisoformat(list_data['created_at'])
                db.session.add(list_item)
        
        # Restore tasks
        for task_data in backup_data['tasks']:
            if not TaskModel.query.get(task_data['id']):
                task = TaskModel(
                    title=task_data['title'],
                    description=task_data['description'],
                    position=task_data['position'],
                    priority=task_data['priority'],
                    list_id=task_data['list_id']
                )
                task.id = task_data['id']
                if task_data['created_at']:
                    task.created_at = datetime.fromisoformat(task_data['created_at'])
                db.session.add(task)
        
        db.session.commit()
        print("✅ Database restored successfully!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate_db.py backup")
        print("  python migrate_db.py restore <backup_file>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        backup_database()
    elif command == "restore" and len(sys.argv) > 2:
        restore_database(sys.argv[2])
    else:
        print("Invalid command!")