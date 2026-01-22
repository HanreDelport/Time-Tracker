import sqlite3
import os

def create_database():
    # Create database folder if it doesn't exist
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('database/timetracker.db')
    cursor = conn.cursor()
    
    # Create Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            total_seconds INTEGER DEFAULT 0,
            is_finished INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("Database created successfully!")
    print("Location: database/timetracker.db")

if __name__ == '__main__':
    create_database()