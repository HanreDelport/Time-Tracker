import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QMessageBox, 
                             QTreeWidgetItem, QPushButton, QHBoxLayout, QWidget, QSystemTrayIcon, QMenu)
from PyQt6 import uic
from database_manager import DatabaseManager
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

class TimeTrackerApp(QMainWindow):

    #INIT FUNCTION

    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('ui/main_window.ui', self)
        
        # Initialize database manager
        self.db = DatabaseManager()

        # Timer for updating running task
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_running_task)
        self.timer.start(1000)  # Update every 1 second
        
        # Track the currently running task
        self.running_task_id = None
        self.running_task_item = None
        self.task_start_time = None
        self.task_elapsed_before_start = 0  # Seconds already accumulated
        
        # Connect toolbar actions to methods
        self.actionAddProject.triggered.connect(self.add_project)
        self.actionExport.triggered.connect(self.export_to_csv)

        # Setup system tray
        self.setup_system_tray()
        
        # Load projects into the tree
        self.load_projects()
        self.setup_tree_context_menu()

        # Set column widths
        self.projectTreeWidget.setColumnWidth(0, 300)  # Name column
        self.projectTreeWidget.setColumnWidth(1, 100)  # Time column
        self.projectTreeWidget.setColumnWidth(2, 250)  # Actions column
        self.projectTreeWidget.setColumnWidth(3, 100)  # Status column
        
        print("App initialized successfully!")


    # ===== PROJECT METHODS =====

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

    # ===== TASK METHODS =====      
   
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

    def create_task_buttons(self, task_item, task_id, is_finished, is_running):
        """Create action buttons for a task"""
        # Create a widget to hold the buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(2, 2, 2, 2)
        button_widget.setLayout(button_layout)
        
        if is_finished:
            # Show only Reopen button for finished tasks
            reopen_btn = QPushButton("Reopen")
            reopen_btn.clicked.connect(lambda: self.reopen_task(task_id))
            button_layout.addWidget(reopen_btn)
        else:
            # Show Start/Pause and Finish buttons for active tasks
            if is_running:
                pause_btn = QPushButton("Pause")
                pause_btn.clicked.connect(lambda: self.pause_task(task_id))
                button_layout.addWidget(pause_btn)
            else:
                start_btn = QPushButton("Start")
                start_btn.clicked.connect(lambda: self.start_task(task_id))
                button_layout.addWidget(start_btn)
            
            finish_btn = QPushButton("Finish")
            finish_btn.clicked.connect(lambda: self.finish_task(task_id))
            button_layout.addWidget(finish_btn)
        
        return button_widget

    def start_task(self, task_id):
        """Start a task timer"""
        # Check if another task is already running
        running_task = self.db.get_running_task()
        if running_task:
            QMessageBox.warning(
                self, 
                "Task Already Running", 
                f"Please pause or finish the currently running task first:\n{running_task[2]}"
            )
            return
        
        # Get current task's total seconds from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT total_seconds FROM tasks WHERE id = ?', (task_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Start the task
        self.running_task_id = task_id
        self.task_start_time = datetime.now()
        self.task_elapsed_before_start = result[0] if result else 0
        
        # Mark task as running in database
        self.db.start_task(task_id)
        
         # Refresh UI
        self.load_projects()
        
        # Find and store reference to the running task item
        self.find_and_store_running_task_item(task_id)
        
        print(f"Started task {task_id}")

    def pause_task(self, task_id):
        """Pause a task timer"""
        if self.running_task_id != task_id:
            return
        
        # Calculate final time
        current_time = datetime.now()
        elapsed_seconds = int((current_time - self.task_start_time).total_seconds())
        total_seconds = self.task_elapsed_before_start + elapsed_seconds
        
        # Update database
        self.db.update_task_time(task_id, total_seconds)
        self.db.pause_task(task_id)
        
        # Stop tracking
        self.running_task_id = None
        self.task_start_time = None
        self.task_elapsed_before_start = 0
        self.running_task_item = None
        
        # Refresh UI
        self.load_projects()
        print(f"Paused task {task_id}")

    def finish_task(self, task_id):
        """Finish a task"""
        # If task is running, pause it first to save the time
        if self.running_task_id == task_id:
            # Calculate final time
            current_time = datetime.now()
            elapsed_seconds = int((current_time - self.task_start_time).total_seconds())
            total_seconds = self.task_elapsed_before_start + elapsed_seconds
            
            # Update database with final time
            self.db.update_task_time(task_id, total_seconds)
            
            # Stop tracking
            self.running_task_id = None
            self.task_start_time = None
            self.task_elapsed_before_start = 0
            self.running_task_item = None
        
        # Mark as finished AND not running
        self.db.finish_task(task_id)
        #self.db.pause_task(task_id)  # Make sure it's not marked as running
        
        # Refresh UI
        self.load_projects()
        print(f"Finished task {task_id}")

    def reopen_task(self, task_id):
        """Reopen a finished task"""
        self.db.reopen_task(task_id)
        self.db.pause_task(task_id)  # Make sure it starts as paused, not running
        self.load_projects()
        print(f"Reopened task {task_id}")

    def find_and_store_running_task_item(self, task_id):
        """Find the tree widget item for the running task"""
        # Search through all projects
        for i in range(self.projectTreeWidget.topLevelItemCount()):
            project_item = self.projectTreeWidget.topLevelItem(i)
            
            # Search through all tasks in this project
            for j in range(project_item.childCount()):
                task_item = project_item.child(j)
                
                # Check if this is our task
                if task_item.data(0, 1) == task_id:
                    self.running_task_item = task_item
                    return

    # ===== TREE METHODS =====           
    
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

            # Add tasks under this project
            for task in tasks:
                task_id, task_name, total_seconds, is_finished, is_running = task
                
                # Create a tree item for the task (child of project)
                task_item = QTreeWidgetItem(project_item)
                task_item.setText(0, task_name)  # Column 0: Task name
                
                # Store the task ID in the item
                task_item.setData(0, 1, task_id)
                
                # Format and display time
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                task_item.setText(1, time_str)  # Column 1: Time
                
                # Column 2: Action buttons
                button_widget = self.create_task_buttons(task_item, task_id, is_finished, is_running)
                self.projectTreeWidget.setItemWidget(task_item, 2, button_widget)
                
                # Column 3: Status
                if is_finished:
                    task_item.setText(3, "Finished")
                elif is_running:
                    task_item.setText(3, "Running")
                else:
                    task_item.setText(3, "Paused")

    def update_project_total_time(self, project_item):
        """Update the total time display for a project"""
        total_seconds = 0
        
        # Sum up all child task times
        for i in range(project_item.childCount()):
            task_item = project_item.child(i)
            time_text = task_item.text(1)  # Get time string like "00:05:23"
            
            # Parse the time string
            time_parts = time_text.split(':')
            if len(time_parts) == 3:
                hours, minutes, seconds = map(int, time_parts)
                total_seconds += hours * 3600 + minutes * 60 + seconds
        
        # Update project's time display
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        project_item.setText(1, time_str)

    # ===== TIMER =====

    def update_running_task(self):
        """Called every second to update the running task's time display"""
        if self.running_task_id is None or self.running_task_item is None:
            return
        
        # Calculate elapsed time since start
        current_time = datetime.now()
        elapsed_seconds = int((current_time - self.task_start_time).total_seconds())
        
        # Total time = previous time + current session time
        total_seconds = self.task_elapsed_before_start + elapsed_seconds
        
        # Update only the display (no database write yet)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Update only the time column in the UI
        self.running_task_item.setText(1, time_str)
        
        # Also update the parent project's total time
        parent_item = self.running_task_item.parent()
        if parent_item:
            self.update_project_total_time(parent_item)

    # ===== SYSTEM TRAY =====

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        #Load icon
        self.tray_icon.setIcon(QIcon("assets/stopwatch.ico"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click tray icon to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation (click)"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        # Check if a task is running
        if self.running_task_id is not None:
            # Show warning
            reply = QMessageBox.warning(
                self,
                "Task Running",
                "A task is currently running. Are you sure you want to close?\n\n"
                "The timer will stop and current progress will be saved.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()  # Cancel the close
                return
            else:
                # Save the running task before closing
                if self.running_task_id:
                    current_time = datetime.now()
                    elapsed_seconds = int((current_time - self.task_start_time).total_seconds())
                    total_seconds = self.task_elapsed_before_start + elapsed_seconds
                    self.db.update_task_time(self.running_task_id, total_seconds)
                    self.db.pause_task(self.running_task_id)
        
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Time Tracker",
            "Application minimized to tray. Double-click the tray icon to restore.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_application(self):
        """Properly quit the application"""
        # Check if a task is running
        if self.running_task_id is not None:
            reply = QMessageBox.warning(
                self,
                "Task Running",
                "A task is currently running. Are you sure you want to quit?\n\n"
                "The timer will stop and current progress will be saved.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
            else:
                # Save the running task
                if self.running_task_id:
                    current_time = datetime.now()
                    elapsed_seconds = int((current_time - self.task_start_time).total_seconds())
                    total_seconds = self.task_elapsed_before_start + elapsed_seconds
                    self.db.update_task_time(self.running_task_id, total_seconds)
                    self.db.pause_task(self.running_task_id)
        
        # Actually quit
        QApplication.quit()


    # ===== EXPORTING =====

    def export_to_csv(self):
        """Handler for Export to CSV button"""
        print("Export to CSV clicked!")
        # We'll implement this later
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())