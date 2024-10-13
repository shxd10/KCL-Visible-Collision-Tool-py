### Gabriela's code (https://github.com/Gabriela-Orzechowska)
import bpy

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