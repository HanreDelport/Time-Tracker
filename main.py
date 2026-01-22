import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
from database_manager import DatabaseManager

class TimeTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('ui/main_window.ui', self)
        
        # Initialize database manager
        self.db = DatabaseManager()
        
        # Connect toolbar actions to methods
        self.actionAddProject.triggered.connect(self.add_project)
        self.actionExport.triggered.connect(self.export_to_csv)
        
        # Load projects into the tree
        self.load_projects()
        
        print("App initialized successfully!")
    
    def add_project(self):
        """Handler for Add Project button"""
        print("Add Project clicked!")
        # We'll implement this in the next step
    
    def export_to_csv(self):
        """Handler for Export to CSV button"""
        print("Export to CSV clicked!")
        # We'll implement this later
    
    def load_projects(self):
        """Load all projects from database into the tree widget"""
        # Clear the tree first
        self.projectTreeWidget.clear()
        
        # Get all projects from database
        projects = self.db.get_all_projects()
        
        print(f"Loaded {len(projects)} projects from database")
        
        # We'll add them to the tree in the next step

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())