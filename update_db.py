import sqlite3

def fix_stuck_tasks():
    conn = sqlite3.connect('database/timetracker.db')
    cursor = conn.cursor()
    
    # Set all tasks to not running
    cursor.execute('UPDATE tasks SET is_running = 0')
    
    conn.commit()
    conn.close()
    
    print("Fixed all stuck running tasks!")

if __name__ == '__main__':
    fix_stuck_tasks()