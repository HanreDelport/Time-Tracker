import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QDialogButtonBox, QTreeWidgetItem
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
        self.setup_tree_context_menu()
        
        print("App initialized successfully!")

    def add_project(self):
       """Handler for Add Project button"""
       # Load the dialog UI
       dialog = uic.loadUi('ui/add_project_dialog.ui')
       dialog.buttonBox.accepted.connect(dialog.accept)
       dialog.buttonBox.rejected.connect(dialog.reject)
       
       # Show the dialog and wait for user response
       if dialog.exec() == QDialog.DialogCode.Accepted:
           # Get the project name from the line edit
           project_name = dialog.projectNameLineEdit.text().strip()
           
           if project_name:
               # Add to database
               project_id = self.db.add_project(project_name)
               print(f"Added project: {project_name} (ID: {project_id})")

               QMessageBox.information(
                dialog,                     # parent window (the dialog)
                "Project Added",             # title of the message box
                f"The project '{project_name}' has been successfully added!"  # message text
            )
               
               # Reload the tree
               self.load_projects()
           else:
               QMessageBox.warning(self, "Error", "Project name cannot be empty!")
       else:
            reply = QMessageBox.question(
            dialog,
            "Cancel",
            "Are you sure you want to cancel adding the project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                dialog.reject()  # Closes the dialog without saving anything
           

   
    def add_task_to_project(self, project_id, project_name):
        """Handler for adding a task to a specific project"""
        # Load the dialog UI
        dialog = uic.loadUi('ui/add_task_dialog.ui')
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        
        # Update dialog title to show which project
        dialog.setWindowTitle(f"Add Task to {project_name}")
        
        # Show the dialog and wait for user response
        result = dialog.exec()
        print("Dialog result:", result)

        if result == QDialog.DialogCode.Accepted:
            # Get the task name from the line edit
            task_name = dialog.taskNameLineEdit.text().strip()
            
            if task_name:
                # Add to database
                task_id = self.db.add_task(project_id, task_name)
                print(f"Added task: {task_name} to project ID {project_id} (Task ID: {task_id})")
                
                # Reload the tree
                self.load_projects()
            else:
                QMessageBox.warning(self, "Error", "Task name cannot be empty!")
        else:            
            reply = QMessageBox.question(
                dialog,
                "Cancel",
                "Are you sure you want to cancel adding the project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                dialog.reject()  # Closes the dialog without saving anything

                
    
    def export_to_csv(self):
        """Handler for Export to CSV button"""
        print("Export to CSV clicked!")
        # We'll implement this later

    def setup_tree_context_menu(self):
        """Setup right-click context menu for the tree"""
        from PyQt6.QtCore import Qt
        self.projectTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.projectTreeWidget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show context menu when right-clicking on tree items"""
        from PyQt6.QtWidgets import QMenu
        
        item = self.projectTreeWidget.itemAt(position)
        if item is None:
            return
        
        # Check if this is a project item (parent is None) or task item (has parent)
        if item.parent() is None:
            # This is a project item
            project_id = item.data(0, 1)
            project_name = item.text(0)
            
            menu = QMenu()
            add_task_action = menu.addAction("Add Task")
            
            action = menu.exec(self.projectTreeWidget.viewport().mapToGlobal(position))
            
            if action == add_task_action:
                self.add_task_to_project(project_id, project_name)
        
    def load_projects(self):
        """Load all projects from database into the tree widget"""
        # Clear the tree first
        self.projectTreeWidget.clear()
        
        # Get all projects from database
        projects = self.db.get_all_projects()
        
        print(f"Loaded {len(projects)} projects from database")
        
        # Add each project to the tree
        for project in projects:
            project_id, project_name = project
            
            # Create a tree item for the project
            project_item = QTreeWidgetItem(self.projectTreeWidget)
            project_item.setText(0, project_name)  # Column 0: Name
            
            # Store the project ID in the item (we'll need this later)
            project_item.setData(0, 1, project_id)  # Store ID in role 1
            
            # Get tasks for this project
            tasks = self.db.get_tasks_for_project(project_id)
            
            # Calculate total time for the project
            total_seconds = sum(task[2] for task in tasks)  # task[2] is total_seconds
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            project_item.setText(1, time_str)  # Column 1: Time
            project_item.setText(3, f"{len(tasks)} task(s)")  # Column 3: Status
            
            # Make project item expandable
            project_item.setExpanded(False)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())