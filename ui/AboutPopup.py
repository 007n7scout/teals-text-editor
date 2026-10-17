import sys

import PySide6
from PySide6.QtWidgets import QApplication, QMessageBox

class AboutPopup(QMessageBox):
     def __init__(self):
        super().__init__()
        self.setWindowTitle("About teal's text editor")
        self.setText("Created by 007n7scout")
        self.setInformativeText(f"v0.9a1 ({sys.platform}) - 17 October 2026\n"
                                f"Python v{sys.version}\n"
                                f"PySide v{PySide6.__version__}\n"
                                f"This really wasn't meant to be a serious project or anything. I "
                                f"just made this for fun. :3\n"
                                f"Check out my GitHub btw: https://github.com/007n7scout/")