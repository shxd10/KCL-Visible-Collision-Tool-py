from BrawlCrate.API import *
from BrawlLib.SSBB.ResourceNodes import *
from BrawlLib.Modeling.Collada import *
from BrawlLib.Wii.Graphics import *
from System.IO import *
import json

with open('data.json', 'r') as file:
    data = json.load(file)

BrawlAPI.OpenFile(data["szs_path"])

root_folder = BrawlAPI.RootNode.FindChild(".")
course_brres = root_folder.FindChild("course_model.brres")
course_node = course_brres.FindChild("3DModels(NW4R)").FindChild("course")

course_node.Replace(data["dae_path"])

shaders_stage = course_node.FindChild("Shaders").FindChild("Shader 0").FindChild("Stage0")

shaders_stage.ColorSelectionA = ColorArg.RasterColor
shaders_stage.ColorSelectionB = ColorArg.Zero
shaders_stage.ColorSelectionC = ColorArg.Zero
shaders_stage.ColorSelectionD = ColorArg.Zero
shaders_stage.ColorScale = TevScale.MultiplyBy1

if not data["lightning"]:
    root_folder.FindChild("posteffect").Remove()

BrawlAPI.SaveFile()

data["done"] = True

with open('data.json', 'w') as file:
    json.dump(data, file)