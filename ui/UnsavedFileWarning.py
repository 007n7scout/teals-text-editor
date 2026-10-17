from PySide6.QtWidgets import *

class UnsavedFileWarning(QMessageBox):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("teal's text editor")
          self.setText("There are unsaved changes in this document! Do you want to keep them?")
          self.setInformativeText("You can choose to save your changes, or delete this document immediately. You can't undo this action.")
          self.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
          self.setDefaultButton(QMessageBox.StandardButton.Save)
          self.ret = self.exec()