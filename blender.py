import bpy
import os

class BlenderKMPProcessor:
    def __init__(self, download_dir, scaling_value=100):
        self.download_dir = os.path.abspath(download_dir)
        self.scaling_value = scaling_value

    def install_plugin(self, zip_plugin_name):
        module_name = "Blender-KMP-Utilities"
        zip_plugin_path = os.path.join(self.download_dir, zip_plugin_name)

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

    def load_szs_file(self):
        for file in os.listdir(self.download_dir):
            if file.endswith(".szs"):
                szs_file_path = os.path.join(self.download_dir, file)
                break
        else:
            raise FileNotFoundError("No .szs file found in the download directory.")

        bpy.ops.kcl.load(filepath=szs_file_path)
        print(f"SZS file '{szs_file_path}' loaded successfully.")
        return szs_file_path

    def clean_scene(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        print("Starting objects deleted.")

    def remove_invalid_objects(self):
        # if i kept these objects, you would see random planes all across the track
        invalid_objects = [
            "ITEM_ROAD", "ITEM_WALL", "FORCE_RECALCULATION",
            "SOUND_TRIGGER", "EFFECT_TRIGGER", "ITEM_STATE_MODIFIER"
        ]
        scene = bpy.context.scene

        for obj in scene.objects:
            if any(invalid_substring in obj.name for invalid_substring in invalid_objects):
                print(f"Invalid object removed: {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)
                

    ### Gabriela's function (https://github.com/Gabriela-Orzechowska)
    def color_conversion(self):
        context = bpy.context
        tex = bpy.data.textures.new("randomAssMaterial", 'IMAGE')
        image = bpy.data.images.new("randomAssImage", width=2, height=2)

        pixels = [[1.0, 1.0, 1.0, 1.0]] * 4  # 2x2 pixels with RGBA (white)
        image.pixels = [chan for px in pixels for chan in px]

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

            mat.use_nodes = True
            txt = mat.node_tree.nodes.new("ShaderNodeTexImage")
            txt.image = image

            principled = next((node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
            if principled:
                mat.node_tree.links.new(principled.inputs['Base Color'], txt.outputs['Color'])

        print("Color conversion completed.")

    def scale_objects(self):
        # scale objects to be good for MKW
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(self.scaling_value, self.scaling_value, self.scaling_value))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        print(f"Scaled all objects by {self.scaling_value}.")

    def export_to_collada(self, szs_file_path):
        szs_name = os.path.basename(szs_file_path).split('.')[-2]
        dae_path = os.path.join(self.download_dir, f"{szs_name}.dae")
        bpy.ops.wm.collada_export(
            filepath=dae_path,
            export_global_forward_selection='-Z',
            export_global_up_selection='Y',
            apply_global_orientation=True,
            use_texture_copies=True
        )
        print(f"Exported to Collada: {dae_path}")

    def process(self):
        self.clean_scene()
        self.install_plugin("Blender-MKW-Utilities.zip")
        szs_file_path = self.load_szs_file()
        self.remove_invalid_objects()
        bpy.ops.object.select_all(action='SELECT')
        self.color_conversion()
        self.scale_objects()
        self.export_to_collada(szs_file_path)

if __name__ == "__main__":
    processor = BlenderKMPProcessor(download_dir="downloads", scaling_value=100)
    processor.process()
