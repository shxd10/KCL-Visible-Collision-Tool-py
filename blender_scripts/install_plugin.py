import bpy
import os

def install_plugin(zip_plugin_path):
    module_name = "Blender-KMP-Utilities"
    
    if module_name in bpy.context.preferences.addons:
        print(f"The add-on '{module_name}' is already installed and enabled.")
        return
        
    if not os.path.exists(zip_plugin_path):
        print(f"Error: ZIP file '{zip_plugin_path}' does not exist.")
        return
    
    try:
        bpy.ops.preferences.addon_install(filepath=zip_plugin_path)
        bpy.ops.preferences.addon_enable(module=module_name)
        bpy.ops.wm.save_userpref()
        
        print(f"Add-on '{module_name}' installed and enabled successfully.")
    except Exception as e:
        print(f"Error installing the plugin: {e}")