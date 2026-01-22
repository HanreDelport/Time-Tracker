import sqlite3

def update_database():
    conn = sqlite3.connect('database/timetracker.db')
    cursor = conn.cursor()
    
    # Add a column to track if a task is currently running
    cursor.execute('''
        ALTER TABLE tasks ADD COLUMN is_running INTEGER DEFAULT 0
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database updated! Added 'is_running' column to tasks table.")

if __name__ == '__main__':
    update_database()