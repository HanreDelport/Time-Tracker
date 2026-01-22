import sqlite3

class DatabaseManager:
    def __init__(self, db_path='database/timetracker.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Create and return a database connection"""
        return sqlite3.connect(self.db_path)
    
    # ===== PROJECT METHODS =====
    
    def add_project(self, name):
        """Add a new project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO projects (name) VALUES (?)', (name,))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id
    
    def get_all_projects(self):
        """Get all projects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM projects ORDER BY created_at DESC')
        projects = cursor.fetchall()
        conn.close()
        return projects
    
    def rename_project(self, project_id, new_name):
        """Rename a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET name = ? WHERE id = ?', (new_name, project_id))
        conn.commit()
        conn.close()
    
    def delete_project(self, project_id):
        """Delete a project and all its tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()
    
    # ===== TASK METHODS =====
    
    def add_task(self, project_id, name):
        """Add a new task to a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (project_id, name) VALUES (?, ?)', (project_id, name))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_tasks_for_project(self, project_id):
        """Get all tasks for a specific project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, total_seconds, is_finished FROM tasks WHERE project_id = ?', (project_id,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def update_task_time(self, task_id, total_seconds):
        """Update the total time for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET total_seconds = ? WHERE id = ?', (total_seconds, task_id))
        conn.commit()
        conn.close()
    
    def finish_task(self, task_id):
        """Mark a task as finished"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET is_finished = 1 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    
    def reopen_task(self, task_id):
        """Reopen a finished task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET is_finished = 0 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    
    def rename_task(self, task_id, new_name):
        """Rename a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET name = ? WHERE id = ?', (new_name, task_id))
        conn.commit()
        conn.close()
    
    def delete_task(self, task_id):
        """Delete a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()