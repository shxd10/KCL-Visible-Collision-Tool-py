from PyQt5.QtWidgets import QMessageBox

def path_popup(program_name):
    msg = QMessageBox()
    msg.setWindowTitle("Invalid path or paths")
    it_them = "it" if "and" not in program_name else "them"
    msg.setText(f"You either don't have {program_name} installed on your PC, or you didn't enter the path to {it_them}. (I also checked for usual paths for {program_name}, but I didn't find {it_them}.)")
    msg.setInformativeText(f"This program provides an automatic installation for {program_name} to your PC. Do you want to do it?\n(Yes for automatic installation, Cancel for going back.)")
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    msg.exec_()
    
def file_popup():
    msg = QMessageBox()
    msg.setWindowTitle("No File Selected")
    msg.setText("You haven't selected a file to process.")
    msg.setInformativeText("Please select a file before running the process.")
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()