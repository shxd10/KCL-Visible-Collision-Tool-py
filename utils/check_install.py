import requests
import os
import zipfile
import shutil
import platform
import subprocess
from PyQt5.QtWidgets import QMessageBox, QDialog, QPushButton, QVBoxLayout, QFileDialog

# Checking for common paths for Blender and BrawlCrate in your PC

def get_common_paths():
    system = platform.system()
    if system == "Windows":
        return {
            "Blender": [
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                os.path.join(os.path.expanduser("~\\Desktop"),"blender.exe"),
                os.path.join(os.path.expanduser("~\\Download"), "blender.exe")
            ],
            "BrawlCrate": [
                os.path.join(os.path.expanduser("~\\Desktop"),"BrawlCrate.exe"),
                os.path.join(os.path.expanduser("~\\Download"), "BrawlCrate.exe")
            ]
        }
    else:
        return {"Blender": [], "BrawlCrate": []}

def find_program_path(program_name):
    common_paths = get_common_paths()
    for path in common_paths.get(program_name, []):
        if os.path.exists(path):
            return path
    return None

def auto_fill_paths():
    blender_path = find_program_path("Blender")
    brawlcrate_path = find_program_path("BrawlCrate")
    
    return {
        "Blender": blender_path,
        "BrawlCrate": brawlcrate_path
    }


# Automatically installing Blender and BrawlCrate

def install_blender(method, parent_window):
    system = platform.system()
    if system == "Windows":
        match method:
            case "portable":
                blender_download_url = "https://www.blender.org/download/release/Blender3.6/blender-3.6.16-windows-x64.zip"
                download_path = os.path.join(os.path.expanduser("~"), "Downloads", "blender-3.6.16-windows-x64.zip")
                extract_path = os.path.join(os.path.expanduser("~"), "Blender3.6-portable")
            case "installer":
                blender_download_url = "https://www.blender.org/download/release/Blender3.6/blender-3.6.16-windows-x64.msi"
                download_path = os.path.join(os.path.expanduser("~"), "Downloads", "blender-3.6.16-windows-x64.msi")
            case _:
                raise ValueError("Invalid method for installing Blender: only 'portable' and 'installer' are supported")
        
        print(f"Downloading Blender from {blender_download_url}...")
        response = requests.get(blender_download_url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Downloaded Blender to {download_path}")

        match method:
            case "portable":
                print(f"Extracting Blender to {extract_path}...")
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Blender extracted to {extract_path}")
                return os.path.join(extract_path, "blender.exe")
            case "installer":
                print("Running Blender installer...")
                QMessageBox.information(parent_window, "Blender Installation", "The Blender installer will now run. Please follow the installation prompts.")
                subprocess.run(["msiexec", "/i", download_path])
                print("Blender installation process completed.")
                
                QMessageBox.information(parent_window, "Locate Blender", "Please locate the installed Blender executable (blender.exe).")
                blender_path = QFileDialog.getOpenFileName(parent_window, "Locate Blender Executable", "", "Executable files (*.exe)")[0]
                if blender_path and os.path.exists(blender_path):
                    return blender_path
                else:
                    raise FileNotFoundError("Blender executable not selected or found.")
    else:
        raise NotImplementedError("This script currently supports only Windows systems.")

def install_brawlcrate():
    system = platform.system()
    if system == "Windows":
        download_url = "https://github.com/soopercool101/BrawlCrate/releases/download/v0.42h1/BrawlCrate.v0.42h1.x86.exe"
        download_path = os.path.join(os.path.expanduser("~\\Download"), "BrawlCrate.v0.42h1.x86.exe")
        
        print(f"Downloading BrawlCrate from {download_url}...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Downloaded BrawlCrate to {download_path}")
        
        print("Running BrawlCrate installer...")
        subprocess.run([download_path], check=True)
        print("BrawlCrate installation process completed.")
        
        return os.path.join(os.path.expanduser("~\\Download"), "BrawlCrate.v0.42h1.x86.exe")
    else:
        raise NotImplementedError("This script currently supports only Windows systems.")
    
def install_program(program_name, parent_window):
    if program_name == "Blender":
        programPath = parent_window.blenderPathEdit.text()
    elif program_name == "BrawlCrate":
        programPath = parent_window.brawlCratePathEdit.text()
    else:
        QMessageBox.warning(parent_window, "Error", "Unknown program")
        return

    if programPath and os.path.exists(programPath) and programPath.endswith(".exe"):
        QMessageBox.information(parent_window, f"{program_name}", f"{program_name} is already installed at the specified path.")
    else:
        reply = QMessageBox.question(parent_window, f"Install {program_name}", f"{program_name} not found. Do you want to install it?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if program_name == "Blender":
                    method_dialog = QDialog(parent_window)
                    method_dialog.setWindowTitle("Blender Installation Method")
                    layout = QVBoxLayout()
                    portable_button = QPushButton("Portable (.zip)")
                    installer_button = QPushButton("Installer (.msi)")
                    layout.addWidget(portable_button)
                    layout.addWidget(installer_button)
                    method_dialog.setLayout(layout)

                    def on_portable():
                        method_dialog.done(0)

                    def on_installer():
                        method_dialog.done(1)

                    portable_button.clicked.connect(on_portable)
                    installer_button.clicked.connect(on_installer)

                    if method_dialog.exec_() == 0:
                        installed_path = install_blender("portable", parent_window)
                    else:
                        installed_path = install_blender("installer", parent_window)
                        
                    parent_window.blenderPathEdit.setText(installed_path)
                elif program_name == "BrawlCrate":
                    installed_path = install_brawlcrate()
                    parent_window.brawlCratePathEdit.setText(installed_path)
                QMessageBox.information(parent_window, "Success", f"{program_name} has been installed successfully.")
            except Exception as e:
                QMessageBox.critical(parent_window, "Error", f"Failed to install {program_name}: {str(e)}")