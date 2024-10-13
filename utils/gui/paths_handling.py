from PyQt5.QtCore import QObject, QSettings
from utils.check_install import auto_fill_paths
import os

class PathsHandling(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("Shxd", "KCLVisibleCollisionTool")
        
        self.initialize_paths()
        
        # Connect path edit changes
        self.main_window.blenderPathEdit.textChanged.connect(self.save_settings)
        self.main_window.brawlCratePathEdit.textChanged.connect(self.save_settings)
        
        # Initialize last used file
        self.load_last_file()

    def initialize_paths(self):
        self.load_settings()
        
        # If paths are still empty, try auto-filling
        if not self.main_window.blenderPathEdit.text() or not self.main_window.brawlCratePathEdit.text():
            paths = auto_fill_paths()
            if paths['Blender'] and not self.main_window.blenderPathEdit.text():
                self.main_window.blenderPathEdit.setText(paths['Blender'])
            if paths['BrawlCrate'] and not self.main_window.brawlCratePathEdit.text():
                self.main_window.brawlCratePathEdit.setText(paths['BrawlCrate'])
            
            self.save_settings()

    def load_settings(self):
        blender_path = self.settings.value("blender_path", "")
        brawlcrate_path = self.settings.value("brawlcrate_path", "")
        
        self.main_window.blenderPathEdit.setText(blender_path)
        self.main_window.brawlCratePathEdit.setText(brawlcrate_path)

    def save_settings(self):
        self.settings.setValue("blender_path", self.main_window.blenderPathEdit.text())
        self.settings.setValue("brawlcrate_path", self.main_window.brawlCratePathEdit.text())

    def load_last_file(self):
        """Load the last used SZS file path"""
        last_path = self.settings.value("last_szs_file")
        if last_path and os.path.exists(last_path):
            self.main_window.selected_file_path = last_path
            self.update_file_display(last_path)

    def save_last_file(self, file_path):
        """Save the last used SZS file path"""
        if file_path and os.path.exists(file_path):
            self.settings.setValue("last_szs_file", file_path)
            self.update_file_display(file_path)

    def update_file_display(self, file_path):
        if hasattr(self.main_window, 'fileBox'):
            self.main_window.fileBox.setText(f"Selected file: {os.path.basename(file_path)}")