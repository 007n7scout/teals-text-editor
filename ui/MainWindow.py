import sys
from PySide6 import QtWidgets
from PySide6.QtGui import QAction, QTextOption, QTextDocument, QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import *
from src.font_manager import load_font
from src.file_reader import read_file, write_file
from src.calendar import get_date_time
from src.settings import settings, set_setting_value, get_setting_value
from ui.UnsavedFileWarning import UnsavedFileWarning
from ui.AboutPopup import AboutPopup

class MainWindow(QMainWindow):
     file = None
     has_unsaved_changes = True

     def __init__(self):
          super().__init__()
          self.resize(900, 700)
          self.showMaximized()
          self.setWindowTitle("teal's text editor")

          self.container = QWidget()
          self.splitter = QSplitter()
          self.master_layout = QHBoxLayout()
          self.text_editor = QTextEdit()
          self.markdown_preview = QTextEdit()
          self.splitter.addWidget(self.text_editor)

          self.status_bar = QStatusBar()
          self.cursor_position_label = QLabel()
          self.cursor_position_label.setStatusTip("Cursor position (line:column)")
          self.word_wrap_mode_label = QLabel()
          self.word_wrap_mode_label.setStatusTip("Soft wraps text to fit window size (toggle using Edit > Word Wrap or "
                                                 "use the keyboard shortcut Ctrl+Alt+Z/Cmd+Option+Z)")
          self.saved_label = QLabel()
          self.saved_label.setStatusTip("Don't forget to save your changes when you're done! ;) (red star indicates unsaved changes)")
          self.language_label = QLabel()
          self.language_label.setStatusTip("Document filetype")
          self.status_bar.addPermanentWidget(self.cursor_position_label)
          self.status_bar.addPermanentWidget(self.word_wrap_mode_label)
          self.status_bar.addPermanentWidget(self.saved_label)
          self.status_bar.addPermanentWidget(self.language_label)
          self.setStatusBar(self.status_bar)

          self.menu_bar = QMenuBar(None if sys.platform == "darwin" else self)
          self.setMenuBar(self.menu_bar)
          self.menu_bar.setNativeMenuBar(True)

          self.file_menu = self.menu_bar.addMenu("File")
          self.edit_menu = self.menu_bar.addMenu("Edit")
          self.search_menu = self.menu_bar.addMenu("Search")
          self.help_menu = self.menu_bar.addMenu("Help")

          self.init_ui()
          self.init_menu_bar()
          self.setCentralWidget(self.splitter)

     def init_menu_bar(self):
          # File menu
          new_action = generate_action(self.file_menu, "New", "Ctrl+N", "Create a new blank file")
          open_action = generate_action(self.file_menu, "Open", "Ctrl+O", "Open a file from disk")
          self.file_menu.addSeparator()
          save_action = generate_action(self.file_menu, "Save", "Ctrl+S", "Save the current file to disk")
          save_as_action = generate_action(self.file_menu, "Save As", "Ctrl+Shift+S", "Save the document as a new file")
          self.file_menu.addSeparator()
          print_action = generate_action(self.file_menu, "Print", "Ctrl+P", "Print the current file")

          # Edit menu
          undo_action = generate_action(self.edit_menu, "Undo", "Ctrl+Z", "Undo the last edit")
          redo_action = generate_action(self.edit_menu, "Redo", "Ctrl+Shift+Z", "Redo the last edit")
          self.edit_menu.addSeparator()
          cut_action = generate_action(self.edit_menu, "Cut", "Ctrl+X", "Cut selected text (copy + delete)")
          copy_action = generate_action(self.edit_menu, "Copy", "Ctrl+C", "Copy selected text to clipboard")
          paste_action = generate_action(self.edit_menu, "Paste", "Ctrl+V", "Paste selected text from clipboard")
          delete_action = generate_action(self.edit_menu, "Delete", "", "Delete selected text from clipboard")
          self.edit_menu.addSeparator()
          select_all_action = generate_action(self.edit_menu, "Select All", "Ctrl+A", "Select entire text")
          insert_time_date_action = generate_action(self.edit_menu, "Time/Date", "", "Insert current time and date")
          self.edit_menu.addSeparator()
          word_wrap_toggle = generate_action(self.edit_menu, "Word Wrap", "Ctrl+Alt+Z", "Toggle soft wrap")
          word_wrap_toggle.setCheckable(True)
          word_wrap_toggle.setChecked(True)

          # Search menu
          find_action = generate_action(self.search_menu, "Find", "Ctrl+F", "Search within the current document")
          find_next_action = generate_action(self.search_menu, "Find Next", "Ctrl+G", "Jump to next occurence")

          # Help menu
          about_action = generate_action(self.help_menu, "About", "", "Display information about this application")
          open_github_action = generate_action(self.help_menu, "Open GitHub page", "", "Does exactly what you might expect")

          # Connections
          def init_menu_bar_events():
               # File menu
               new_action.triggered.connect(self.new_file)
               open_action.triggered.connect(self.open_file)
               save_action.triggered.connect(self.save_file)
               save_as_action.triggered.connect(self.save_as)
               print_action.triggered.connect(self.print_dialog)

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
               word_wrap_toggle.toggled.connect(lambda: set_setting_value("Editor/WordWrapEnabled", word_wrap_toggle.isChecked()))

               # Help menu
               about_action.triggered.connect(lambda: AboutPopup().exec())
          init_menu_bar_events()
          self.word_wrap_mode_label.setText("Word Wrap" if word_wrap_toggle.isChecked() else "No Wrap")

     def init_ui(self):
          # Text edit widget
          self.text_editor.setAcceptRichText(False)
          self.text_editor.setAcceptDrops(False)
          self.text_editor.setFont(load_font("Unifont", 18, "otf"))
          self.text_editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
          self.status_bar.setFont(load_font("Unifont", 16, "otf"))
          self.status_bar.setStyleSheet(read_file("stylesheets/StatusBar.css"))
          self.text_editor.textChanged.connect(self.on_text_changed)
          self.markdown_preview.setReadOnly(True)
          self.splitter.setHandleWidth(10)
          self.markdown_preview.setFont(load_font("Inter", 18))
          self.text_editor.setWordWrapMode(QTextOption.WrapMode.WordWrap if get_setting_value("Editor/WordWrapEnabled") else QTextOption.WrapMode.NoWrap)
          self.status_bar.showMessage("")

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
          self.render_markdown()
          self.setWindowTitle(f"teal's text editor - {'untitled' if self.file is None else self.file.split('/')[-1]}")
          self.language_label.setText(
               self.get_file_extension()
          )

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
                    if len(file_content) >= 2000000:
                         popup = QMessageBox()
                         popup.setText("Woah! It looks like the file you are attempting to open is too large! Do you "
                                       "still want to proceed?")
                         popup.setInformativeText("You can choose to open this file now, but please be aware that "
                                                  "the program may be more likely to crash.")
                         popup.setDetailedText(f"File size: {len(file_content):,} bytes\nNote: Attempting to open a file "
                                               f"that's at least two megabytes large will trigger this warning.")
                         popup.setDefaultButton(QMessageBox.StandardButton.No)
                         popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                         ret = popup.exec()
                         if ret == QMessageBox.StandardButton.No:
                              return None
                    self.text_editor.setText(file_content)
                    self.file = selected_file
                    if selected_file.endswith('.md') or selected_file.endswith('.html'):
                         self.toggle_markdown_preview(True)
                    else:
                         self.toggle_markdown_preview(False)
                    self.on_text_changed()
                    return None
               except UnicodeDecodeError:
                    popup = QMessageBox()
                    popup.setText(f"The file '{selected_file.split('/')[-1]}' may be a binary file, or contain unsupported characters.")
                    popup.setInformativeText(""
                                             "For now, only UTF-8 encoded files are supported. "
                                             "Support for other file encodings may come in the future, but "
                                             "that'll have to wait for now... :(")
                    popup.setIconPixmap(QPixmap("../images/binaryFile.png"))
                    popup.exec()
                    return None
               except IsADirectoryError:
                    return None
          return None

     def save_file(self):
          if self.file is not None:
               write_file(self.file, self.text_editor.toPlainText())
               self.on_text_changed()
          else:
               self.save_as()

     def new_file(self):
          if self.text_editor.toPlainText() != "" and self.text_editor.toPlainText() != read_file(self.file):
               warning = UnsavedFileWarning()
               if warning.ret == QMessageBox.StandardButton.Save:
                    self.save_file()
               elif warning.ret == QMessageBox.StandardButton.Cancel:
                    return None
          self.file = None
          self.text_editor.setText("")
          self.on_text_changed()
          return None

     def save_as(self):
          file_path = QFileDialog.getSaveFileName(None, "Save File", "./", "*.*")
          if file_path != ():
               self.file = file_path[0]
               write_file(file_path[0], self.text_editor.toPlainText())
               self.on_text_changed()

     def print_dialog(self):
          printer = QPrinter()
          print_dialog = QPrintDialog(printer, self)
          if print_dialog.exec() == QPrintDialog.Accepted:
               # TODO: please someone remind me to test this next week
               #  my printers broken and im to lazy to fix it🥀
               self.text_editor.document().print_(printer)

     def render_markdown(self):
          text_content = self.text_editor.toPlainText()
          if self.get_file_extension() == "HTML":
               self.markdown_preview.setHtml(text_content)
          else:
               self.markdown_preview.setMarkdown(text_content)

     def toggle_markdown_preview(self, state):
          if state:
               self.splitter.addWidget(self.markdown_preview)
               self.render_markdown()
          else:
               self.markdown_preview.setParent(None)

     def get_file_extension(self):
          if self.file is None:
               return "Plain text"
          match self.file.split('.')[-1]:
               case "md":
                    return "Markdown"
               case "html":
                    return "HTML"
               case _:
                    return "Plain text"

def generate_action(menu: QMenu, text="Action", shortcut=None, status_tip="", icon=None):
     action = menu.addAction(text)
     action.setStatusTip(status_tip)
     if shortcut is not None: action.setShortcut(shortcut)
     if icon is not None: action.setShortcut(icon)
     return action