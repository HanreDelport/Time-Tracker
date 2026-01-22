import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

class TimeTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('ui/main_window.ui', self)
        
        print("UI loaded successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())  