import bpy
import sys
import os

# Doing this to import other packages from the same directory
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.append(project_path)

from blender_scripts import install_plugin, color_conversion

def main():
    download_dir = os.path.abspath("downloads")
    zip_plugin_path = os.path.join(download_dir, "Blender-MKW-Utilities.zip")
    
    for file in os.listdir(download_dir):
        if file.endswith(".szs"):
            szs_file_path = os.path.join(download_dir, file)
            break
    
    print(f"Installing plugin from '{zip_plugin_path}'...")
    install_plugin.install_plugin(zip_plugin_path)
    
    # Select and delete all the starting objects and delete them (like the cube and the camera)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("Starting objects deleted")
    
    # Load the SZS file 
    bpy.ops.kcl.load(filepath=szs_file_path) #kcl.load is the func provided by the plugin
    print("SZS file loaded")
    
    scene = bpy.context.scene
    
    # They arent really "invalid", but you need to delete them
    invalid_objects = ["ITEM_ROAD", "ITEM_WALL", "FORCE_RECALCULATION", "SOUND_TRIGGER", "EFFECT_TRIGGER", "ITEM_STATE_MODIFIER"]
    
    for obj in scene.objects:
        # Check if the object name contains a string in the invalid_objects list and remove them
        if any(invalid_substring in obj.name for invalid_substring in invalid_objects):
            print(f"Invalid object removed: {obj.name}")
            bpy.data.objects[obj.name].select_set(True)
            bpy.data.objects.remove(obj)
            
    # select all and run the color conversion script
    bpy.ops.object.select_all(action='SELECT')
    color_conversion.color_conversion()
    print("Color conversion completed")
    
    # scaling all objects for the right size in mkwii
    scaling_value = 100
    bpy.ops.transform.resize(value=(scaling_value, scaling_value, scaling_value))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(f"Scaled all objects by {scaling_value}")
    
    # export as collada 
    szs_name = os.path.basename(szs_file_path).split('.')[-2]
    dae_path = os.path.join(os.path.abspath(os.path.basename(download_dir)), f"{szs_name}.dae")
    bpy.ops.wm.collada_export(
        filepath=dae_path,
        export_global_forward_selection='-Z',
        export_global_up_selection='Y',
        apply_global_orientation=True,
        use_texture_copies=True
        )

if __name__ == "__main__":
    main()
