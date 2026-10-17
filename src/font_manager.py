import os
import sys
from PySide6.QtGui import QFontDatabase, QFont

file_dir = os.path.dirname(__file__)
file_dir = file_dir[:file_dir.rfind("/")]

def load_font(font_name, font_size=14, font_type="ttf"):
     font_id = QFontDatabase.addApplicationFont(f"{file_dir}/fonts/{font_name}.{font_type}")
     if font_id != -1:
          families = QFontDatabase.applicationFontFamilies(font_id)
          font_family = families[0]
          return QFont(font_family, font_size)
     else:
          print(f"Failed to load font {font_name}! :(")
          return QFont("Menlo", 14)