import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QDialogButtonBox
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
        self.actionAddProject.triggered.connect(self.handle_add_buttons)
        self.actionExport.triggered.connect(self.export_to_csv)
        
        # Load projects into the tree
        self.load_projects()
        
        print("App initialized successfully!")
    
    def handle_add_buttons(self):
        # Load the dialog UI
       dialog = QDialog(self)
       uic.loadUi('ui/add_project_dialog.ui', dialog)
      

       dialog.buttonBox.accepted.connect(lambda: self.add_project(dialog))
       #dialog.buttonBox.rejected.connect(dialog.reject)
       dialog.exec()

    
    def add_project(self, dialog):
       """Handler for Add Project button"""      
       # Get the project name from the line edit
       project_name = dialog.projectNameLineEdit.text().strip()
        
       if project_name:
           # Add to database
           project_id = self.db.add_project(project_name)
           print(f"Added project: {project_name} (ID: {project_id})")
            
           # Reload the tree
           self.load_projects()

           dialog.accept()
       else:
           QMessageBox.warning(self, "Error", "Project name cannot be empty!")
           
    
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