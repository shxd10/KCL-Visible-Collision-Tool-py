import bpy
import os

### Gabriela's function (https://github.com/Gabriela-Orzechowska)
def color_conversion():
    context = bpy.context
    tex = bpy.data.textures.new("randomAssMaterial", 'IMAGE')
    image = bpy.data.images.new("randomAssImage", width=2, height=2)
    
    pixels = [None] * 2 * 2
    for x in range(2):
        for y in range(2):
            # assign RGBA to something useful
            r = 1.0
            g = 1.0
            b = 1.0
            a = 1.0

            pixels[(y * 2) + x] = [r, g, b, a]

    # flatten list
    pixels = [chan for px in pixels for chan in px]

    # assign pixels
    image.pixels = pixels
        
    # write image
    image.filepath_raw = "/tmp/temp.png"
    image.file_format = 'PNG'
    image.save()
    tex.image = image
        
    for obj in context.selected_objects:
        mesh = obj.data
        mat = mesh.materials[0]
        mat.use_nodes = False
        
        for c in mesh.color_attributes:
            mesh.color_attributes.remove(c)
        mesh.color_attributes.new(name="Vertex Colors", type='BYTE_COLOR', domain='CORNER')
       
        v = mat.diffuse_color
        mat.use_nodes = True

        for vcol in mesh.color_attributes[0].data:
            for i in range(len(vcol.color)-1):
                vcol.color[i] = v[i]
        
        txt = mat.node_tree.nodes.new("ShaderNodeTexImage")
        txt.image = image
        links = mat.node_tree.links
        principled = None
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
        links.new(principled.inputs['Base Color'], txt.outputs['Color'])
        
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

def main():
    download_dir = os.path.abspath("downloads")
    zip_plugin_path = os.path.join(download_dir, "Blender-MKW-Utilities.zip")
    
    for file in os.listdir(download_dir):
        if file.endswith(".szs"):
            szs_file_path = os.path.join(download_dir, file)
            break
    
    print(f"Installing plugin from '{zip_plugin_path}'...")
    install_plugin(zip_plugin_path)
    
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
    color_conversion()
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