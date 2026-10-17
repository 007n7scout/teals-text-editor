from PySide6.QtCore import QCoreApplication, QSettings

QCoreApplication.setOrganizationName("007n7scout")
QCoreApplication.setOrganizationDomain("github.com/007n7scout")
QCoreApplication.setApplicationName("teal's text editor")
settings = QSettings()

def set_setting_value(key, value):
     settings.setValue(key, value)

def get_setting_value(key):
     value = settings.value(key)
     if value == 0:
          return None
     return value