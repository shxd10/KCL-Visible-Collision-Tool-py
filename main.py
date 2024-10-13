import sys
import webbrowser
import subprocess
import os
import shutil
import requests
import json
import time
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from utils.gui import paths_handling, popups, file_handling
from utils.check_install import install_program

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file automatically
        try:
            uic.loadUi('gui.ui', self)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "UI file 'gui.ui' not found.")
            sys.exit(1)
        
        self.selected_file_path = None
        self.download_dir = os.path.abspath("downloads")
        self.plugin_name = "Blender-MKW-Utilities.zip"
        self.plugin_path = os.path.join(self.download_dir, self.plugin_name)
        self.szs_path = None
        
        self.progressBar.hide()
        self.statusLabel.hide()
        self.downloadBox.hide()
        self.downloadButton.clicked.connect(self.download_result)
        
        # Set up the file and path handling
        self.file_handling = file_handling.FileHandling(self)
        self.file_handling.setup_connections()
        self.file_handling.file_selected.connect(self.on_file_selected)
        self.paths_handling = paths_handling.PathsHandling(self)
        self.paths_handling.load_settings()
        
        # Connect the menuBar actions
        actions = {
            self.actionSZS: lambda: self.file_handling.open_file_dialog("Select SZS File", "szs"),
            self.actionGithub: lambda: webbrowser.open("https://github.com/shxd10/KCL-Visible-Collision-Tool"),
            self.actionDiscord: lambda: webbrowser.open("https://discordapp.com/users/812615237168660481"),
            self.actionTutorial: lambda: webbrowser.open("https://www.dropbox.com/scl/fo/36pjicleqj7ilsdfzpocr/AO93sa02dgbczOQBws9u3cU?rlkey=y0a6b5s8jaxsf1xah9dx8n3iz&st=aoeyayp1&dl=1")
        }
        for action, function in actions.items():
            action.triggered.connect(function)
        
        # Connect the buttons to their respective functions
        self.blenderCheckButton.clicked.connect(lambda: install_program("Blender", self))
        self.brawlCrateCheckButton.clicked.connect(lambda: install_program("BrawlCrate", self))
        self.mainButton.clicked.connect(self.run_process)
        
    def on_file_selected(self, file_path):
        self.selected_file_path = file_path
        self.paths_handling.save_last_file(file_path)
        print(f"File selected: {file_path}")
        
    def show_progress(self, show=True):
        if show:
            self.fileBox.hide()
            self.downloadBox.hide()
            self.progressBar.show()
            self.statusLabel.show()
        else:
            self.progressBar.hide()
            self.statusLabel.hide()
            if self.done:
                self.downloadBox.show()
            else:
                self.fileBox.show()

    def show_download_box(self):
        self.fileBox.hide()
        self.progressBar.hide()
        self.statusLabel.hide()
        self.downloadBox.show()

    def update_progress(self, value, status_text):
        self.progressBar.setValue(value)
        self.statusLabel.setText(status_text)

    def download_result(self):
        try:
            szs_name = f"{[file for file in os.listdir(self.download_dir) if file.endswith(".szs")][0].split(".szs")[0]} (Visible Collision)"
            print(f"Downloading {szs_name}...")
            
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save File",
                os.path.join(os.path.expanduser("~"), "Downloads", szs_name),
                "SZS files (*.szs);;All Files (*)"
            )
            
            if file_name:
                shutil.copy2(self.szs_path, file_name)
                QMessageBox.information(self, "Success", "File downloaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download file: {str(e)}")

    def run_process(self):
        print("Run button clicked")
        if not self.validate_inputs():
            return

        self.done = False
        self.show_progress()
        self.update_progress(0, "Starting process...")

        use_lightning = self.lightToggle.isChecked()
        blender_path = self.blenderPathEdit.text()
        brawlcrate_path = self.brawlCratePathEdit.text()

        try:
            self.update_progress(10, "Creating download directory...")
            if not os.path.exists(self.download_dir):
                os.mkdir(self.download_dir)
                print(f"Folder '{self.download_dir}' created.")
            
            self.update_progress(20, "Cleaning up old files...")
            for file in os.listdir(self.download_dir):
                if file.endswith((".szs", ".dae", ".png")):
                    os.remove(os.path.join(self.download_dir, file))
                
            self.update_progress(30, "Copying SZS file...")
            self.szs_path = os.path.join(self.download_dir, os.path.basename(self.selected_file_path))
            shutil.copy2(self.selected_file_path, self.szs_path)
            
            # Install plugin
            self.update_progress(40, "Installing Blender plugin...")
            self.install_plugin()
            
            # Run Blender process
            self.update_progress(45, "Running Blender process...")
            self.update_progress(50, "Running Blender process...")
            blender_subprocess = subprocess.Popen([blender_path, 
                            '--background',
                            '--python',
                            os.path.abspath('blender.py'),])
            blender_subprocess.wait()
            blender_subprocess.terminate()
            print("Blender process terminated")
            
            self.update_progress(70, "Running Brawlcrate process...")
            self.update_progress(80, "Running Brawlcrate process...")
            brawlcrate_script = os.path.abspath('brawlcrate.py')
            loaders_folder = os.path.join(os.path.dirname(brawlcrate_path), "BrawlAPI/Loaders")
            shutil.copy2(brawlcrate_script, loaders_folder)
            print("Brawlcrate script copied to BrawlAPI loaders folder")
            
            dae_path = os.path.join(self.download_dir, [file for file in os.listdir(self.download_dir) if file.endswith(".dae")][0])
            # Creating .json file so i can access values in the Loaders folder
            json_object = json.dumps({"szs_path": self.szs_path,
                                      "loaders_path": loaders_folder,
                                      "dae_path": dae_path,
                                      "lightning": use_lightning,
                                      "done": False
                                      }, indent=4)
            with open("data.json", "w") as outfile:
                outfile.write(json_object)
            print("JSON file created")
            
            brawlcrate_subprocess = subprocess.Popen(brawlcrate_path)
            
            while True:
                with open("data.json", "r") as json_file:
                    json_data = json.load(json_file)
                
                if json_data["done"]:
                    brawlcrate_subprocess.terminate()
                    break
                
                time.sleep(2)
                
            print("Brawlcrate process terminated")
            os.remove(os.path.join(loaders_folder, "brawlcrate.py"))
            os.remove("data.json")
            self.done = True
            self.update_progress(100, "Process completed successfully!")
            
            QTimer.singleShot(1500, self.show_download_box)
            
        except Exception as e:
            self.update_progress(100, f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while running Blender or BrawlCrate: {str(e)}")
            print(f"Error running Blender or BrawlCrate: {e}")
            # Show file box after a delay
            QTimer.singleShot(2000, lambda: self.show_progress(False))
        
    def install_plugin(self):
        plugin_url = "https://github.com/Gabriela-Orzechowska/Blender-MKW-Utilities/releases/download/v0.1.13.5/Blender-MKW-Utilities-v0.1.13.5.zip"
        
        try:
            if os.path.exists(self.plugin_path):
                return
            
            print(f"Downloading plugin from {plugin_url}...")
            response = requests.get(plugin_url, stream=True)
            response.raise_for_status()
            
            with open(self.plugin_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Plugin downloaded to {self.plugin_path}")
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Download Error", f"Failed to download plugin: {str(e)}")
            print(f"Error downloading plugin: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while installing the plugin: {str(e)}")
            print(f"Error installing plugin: {e}")

    def validate_inputs(self):
        if self.selected_file_path is None:
            popups.file_popup()
            return False

        missing_paths = []
        if not self.blenderPathEdit.text():
            missing_paths.append("Blender")
        if not self.brawlCratePathEdit.text():
            missing_paths.append("BrawlCrate")

        if missing_paths:
            popups.path_popup(" and ".join(missing_paths))
            return False

        return True

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())