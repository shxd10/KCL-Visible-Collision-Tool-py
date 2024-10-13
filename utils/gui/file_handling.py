from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class FileHandling(QObject):
    file_selected = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def setup_connections(self):
        self.parent.setAcceptDrops(True)
        self.parent.fileBox.mousePressEvent = self.file_box_click
        self.parent.blenderPathEdit.mouseDoubleClickEvent = lambda event: self.open_path_dialog(self.parent.blenderPathEdit, "Select Blender Executable", "exe")
        self.parent.brawlCratePathEdit.mouseDoubleClickEvent = lambda event: self.open_path_dialog(self.parent.brawlCratePathEdit, "Select BrawlCrate Executable", "exe")

    # Drag and Drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if f.lower().endswith(('.szs')):
                self.file_processing(f)
                break
    
    def file_box_click(self, event):
        self.open_file_dialog("Select SZS File", "szs")

    def open_file_dialog(self, title, extension):
        if not extension:
            extension = ""
        file_filter = f"{extension.upper()} Files (*.{extension})" if extension else "All Files (*.*)"
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self.parent, title, "", file_filter)
        if file:
            self.file_processing(file)

    def open_path_dialog(self, textbox, title, extension):
        if not extension:
            extension = ""
        file_filter = f"{extension.upper()} Files (*.{extension})" if extension else "All Files (*.*)"
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self.parent, title, "", file_filter)
        if file:
            textbox.setText(file)

    def file_processing(self, file_path):
        self.parent.fileBox.setText(f"Selected file: {file_path}")
        self.file_selected.emit(file_path)