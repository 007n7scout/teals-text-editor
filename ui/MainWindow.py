from PySide6 import QtWidgets
from PySide6.QtGui import QAction, QTextOption
from PySide6.QtWidgets import *
from src.font_manager import load_font
from src.file_reader import read_file, write_file
from src.calendar import get_date_time
from ui.UnsavedFileWarning import UnsavedFileWarning

class MainWindow(QMainWindow):
     file = None
     has_unsaved_changes = True

     def __init__(self):
          super().__init__()
          self.resize(900, 700)
          self.showMaximized()
          self.setWindowTitle("teal's text editor")

          self.text_editor = QTextEdit()

          self.status_bar = QStatusBar(self)
          self.cursor_position_label = QLabel()
          self.cursor_position_label.setToolTip("Cursor position (row:column)")
          self.word_wrap_mode_label = QLabel()
          self.word_wrap_mode_label.setToolTip("To toggle word wrap mode, go to Edit > Word Wrap")
          self.saved_label = QLabel()
          self.saved_label.setToolTip("Don't forget to save your work when you're done! ;)")
          self.status_bar.addPermanentWidget(self.cursor_position_label)
          self.status_bar.addPermanentWidget(self.word_wrap_mode_label)
          self.status_bar.addPermanentWidget(self.saved_label)
          self.setStatusBar(self.status_bar)

          self.menu_bar = QMenuBar()
          self.menu_bar.setNativeMenuBar(True)

          self.file_menu = self.menu_bar.addMenu("File")
          self.edit_menu = self.menu_bar.addMenu("Edit")
          self.search_menu = self.menu_bar.addMenu("Search")

          self.init_ui()
          self.init_menu_bar()
          self.setCentralWidget(self.text_editor)

     def init_menu_bar(self):
          # File menu
          new_action = generate_action(self.file_menu, "New", "Ctrl+N")
          open_action = generate_action(self.file_menu, "Open", "Ctrl+O")
          save_action = generate_action(self.file_menu, "Save", "Ctrl+S")
          save_as_action = generate_action(self.file_menu, "Save As", "Ctrl+Shift+S")
          print_action = generate_action(self.file_menu, "Print", "Ctrl+P")

          # Edit menu
          undo_action = generate_action(self.edit_menu, "Undo", "Ctrl+Z")
          redo_action = generate_action(self.edit_menu, "Redo", "Ctrl+Shift+Z")
          self.edit_menu.addSeparator()
          cut_action = generate_action(self.edit_menu, "Cut", "Ctrl+X")
          copy_action = generate_action(self.edit_menu, "Copy", "Ctrl+C")
          paste_action = generate_action(self.edit_menu, "Paste", "Ctrl+V")
          delete_action = generate_action(self.edit_menu, "Delete")
          self.edit_menu.addSeparator()
          select_all_action = generate_action(self.edit_menu, "Select All", "Ctrl+A")
          insert_time_date_action = generate_action(self.edit_menu, "Time/Date", "")
          self.edit_menu.addSeparator()
          word_wrap_toggle = generate_action(self.edit_menu, "Word Wrap", "Ctrl+Alt+Z")
          word_wrap_toggle.setCheckable(True)
          word_wrap_toggle.setChecked(True)

          # Search menu
          find_action = generate_action(self.search_menu, "Find", "Ctrl+F")
          find_next_action = generate_action(self.search_menu, "Find Next", "Ctrl+G")

          # Connections
          def init_menu_bar_events():
               # File menu
               open_action.triggered.connect(self.open_file)
               save_action.triggered.connect(self.save_file)

               # Edit menu
               undo_action.triggered.connect(self.text_editor.undo)
               redo_action.triggered.connect(self.text_editor.redo)
               cut_action.triggered.connect(self.text_editor.cut)
               copy_action.triggered.connect(self.text_editor.copy)
               paste_action.triggered.connect(self.text_editor.paste)
               select_all_action.triggered.connect(self.text_editor.selectAll)
               insert_time_date_action.triggered.connect(lambda: self.text_editor.append(get_date_time()))
               word_wrap_toggle.toggled.connect(lambda: self.text_editor.setWordWrapMode(
                    QTextOption.WrapMode.WordWrap if word_wrap_toggle.isChecked() else QTextOption.WrapMode.NoWrap
               ))
               word_wrap_toggle.toggled.connect(lambda: self.word_wrap_mode_label.setText(
                    "Word Wrap" if word_wrap_toggle.isChecked() else "No Wrap"
               ))
          init_menu_bar_events()
          self.word_wrap_mode_label.setText("Word Wrap" if word_wrap_toggle.isChecked() else "No Wrap")

     def init_ui(self):
          # Text edit widget
          self.text_editor.setAcceptRichText(False)
          self.text_editor.setFont(load_font("Unifont", 18, "otf"))
          self.text_editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
          self.status_bar.setFont(load_font("Unifont", 16, "otf"))
          self.status_bar.setStyleSheet(read_file("stylesheets/StatusBar.css"))
          self.text_editor.textChanged.connect(self.on_text_changed)

          self.on_cursor_position_changed()
          self.on_text_changed()

     def on_cursor_position_changed(self):
          self.cursor_position_label.setText(
               f"{self.text_editor.textCursor().blockNumber()}:{self.text_editor.textCursor().positionInBlock()}"
          )

     def on_text_changed(self):
          if self.file is not None and read_file(self.file) == self.text_editor.toPlainText():
               self.saved_label.setText("✓")
               self.saved_label.setStyleSheet("color: green")
          else:
               self.saved_label.setText("*")
               self.saved_label.setStyleSheet("color: red")

     def open_dialog(self):
          dialog = QFileDialog(self)
          # dialog.setNameFilter("Plain Text Files (*.txt)")
          dialog.setFileMode(QFileDialog.FileMode.AnyFile)
          dialog.setViewMode(QFileDialog.ViewMode.Detail)
          dialog.setWindowTitle("Select file to open...")
          dialog.exec()
          return dialog.selectedFiles()

     def open_file(self):
          selected_file = self.open_dialog()[0]
          if selected_file:
               try:
                    file_content = read_file(selected_file)
                    self.text_editor.setText(file_content)
                    self.file = selected_file
                    self.on_text_changed()
                    return None
               except UnicodeDecodeError:
                    popup = QMessageBox()
                    popup.setText(f"The file '{selected_file.split('/')[-1]}' may be a binary file, or contain unsupported characters.")
                    popup.setInformativeText(""
                                             "For now, only UTF-8 encoded files are supported. "
                                             "Support for other file encodings may come in the future, but "
                                             "that'll have to wait for now... :(")
                    popup.exec()
                    return None

     def save_file(self):
          if self.file is not None:
               write_file(self.file, self.text_editor.toPlainText())
               self.on_text_changed()

def generate_action(menu: QMenu, text="Action", shortcut=None, icon=None):
     action = menu.addAction(text)
     if shortcut is not None: action.setShortcut(shortcut)
     if icon is not None: action.setShortcut(icon)
     return action