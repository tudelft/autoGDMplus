""" isaac_asset_placer.py
Just like blender_asset_placer.py this script takes in the available recipies and
generates .usd files accordingly.
"""
import sys # get recipe and mockup scene dir
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all the args after " -- "
recipe_dir = argv[0]    # recipe folder
usd_dir = argv[1]  # isaac sim export folder

# Launch Isaac Sim before any other imports
# Default first two lines in any standalone application
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": True})

import os, platform
import glob
import json
import random
import numpy as np
import carb
import omni.ext
import omni.ui as ui
from omni.ui.workspace_utils import RIGHT
from pxr import Usd, UsdGeom, UsdLux, Gf
# from wh_recipes import warehouse_recipe_custom as wh_rec
# from wh_recipes import warehouse_recipe_simple as wh_simp

class wh_helpers():
    def __init__(self):
        # NUCLEUS_SERVER_CUSTOM = "~/Omniverse_content/ov-industrial3dpack-01-100.1.1/"
        # SIMPLE_WAREHOUSE = "~/Omniverse_content/isaac-simple-warehouse/"
        self._system = platform.system()
        self.usd_save_dir = usd_dir

    def config_environment(self):
        for prim in self._stage.Traverse():
            if '/Environment/' in str(prim):
                prim.SetActive(False)
        # self.create_rectangular_light(translate, scale)
    
    def create_distant_light(self):
        environmentPath = '/Environment'
        lightPath = environmentPath + '/distantLight'
        prim = self._stage.DefinePrim(environmentPath, 'Xform')
        distLight = UsdLux.DistantLight.Define(self._stage, lightPath)
        distLight.AddRotateXYZOp().Set(Gf.Vec3f(315,0,0))
        distLight.CreateColorTemperatureAttr(6500.0)
        if self._system == "Linux":
            distLight.CreateIntensityAttr(6500.0)
        else:
            distLight.CreateIntensityAttr(3000.0)
        distLight.CreateAngleAttr(1.0)
        lightApi = UsdLux.ShapingAPI.Apply(distLight.GetPrim())
        lightApi.CreateShapingConeAngleAttr(180)

    # TODO: optional, implement this func correctly
    def create_rectangular_light(self, translate, scale):
        environmentPath = '/Environment'
        lightPath = environmentPath + '/rectLight'
        prim = self._stage.DefinePrim(environmentPath, 'Xform')
        rectLight = UsdLux.RectLight.Define(self._stage, lightPath)
        # rectLight = UsdLux.RectLight.Define(prim, lightPath)
        # rectLight.AddScaleOp().Set(Gf.Vec3f(scale[0],scale[1],scale[2]))
        # rectLight.translateOp().Set(Gf.Vec3f(translate[0],translate[1],translate[2]))
        # distLight.AddRotateXYZOp().Set(Gf.Vec3f(315,0,0))
        # UsdGeom.XformCommonAPI(rectLight).SetTranslate(translate)
        # UsdGeom.XformCommonAPI(rectLight).SetScale(scale)
        print("rectlight!!!")
        rectLight.CreateColorTemperatureAttr(6500.0)
        if self._system == "Linux":
            rectLight.CreateIntensityAttr(6500.0)
        else:
            rectLight.CreateIntensityAttr(3000.0)
        #distLight.CreateAngleAttr(1.0)
        lightApi = UsdLux.ShapingAPI.Apply(rectLight.GetPrim())
        #lightApi.CreateShapingConeAngleAttr(180)

    # spawn_prim function takes in a path, XYZ position, orientation, a name and spawns the USD asset in path with
    # the input name in the given position and orientation inside the world prim as an XForm
    def spawn_prim(self, path, translate, rotate, name, scale=Gf.Vec3f(1.0, 1.0, 1.0)):
        world = self._stage.GetDefaultPrim()
        # Creating an XForm as a child to the world prim
        asset = UsdGeom.Xform.Define(self._stage, f"{str(world.GetPath())}/{name}")
        # Checking if asset already has a reference and clearing it
        asset.GetPrim().GetReferences().ClearReferences()
        # Adding USD in the path as reference to this XForm
        asset.GetPrim().GetReferences().AddReference(f"{path}")
        # Setting the Translate and Rotate
        UsdGeom.XformCommonAPI(asset).SetTranslate(translate)
        UsdGeom.XformCommonAPI(asset).SetRotate(rotate)
        UsdGeom.XformCommonAPI(asset).SetScale(scale)
        # Returning the Xform if needed
        return asset

    # Clear stage function
    def clear_stage_old(self):
        #Removing all children of world except distant light
        self.get_root()
        world = self._stage.GetDefaultPrim()
        doesLightExist = self._stage.GetPrimAtPath('/Environment/distantLight').IsValid()
        # config environment
        if doesLightExist == False:
            self.config_environment()
        # clear scene
        for i in world.GetChildren():
            if i.GetPath() == '/Environment/distantLight' or i.GetPath() == '/World':
                continue
            else:
                self._stage.RemovePrim(i.GetPath())
    
    def clear_stage(self):
        self.get_root()
        # Removing all children of world 
        world = self._stage.GetDefaultPrim()
        for i in world.GetChildren():
            if i.GetPath() == '/World':
                continue
            else:
                self._stage.RemovePrim(i.GetPath())

    # gets stage
    def get_root(self):
        self._stage = omni.usd.get_context().get_stage()
        #UsdGeom.Tokens.upAxis(self._stage, UsdGeom.Tokens.y) # Set stage upAxis to Y
        world_prim = self._stage.DefinePrim('/World', 'Xform') # Create top-level World Xform primitive
        self._stage.SetDefaultPrim(world_prim)                 # Set as default primitive

    # save stage to .usd
    def save_stage(self, fname):
        save_loc = f"{self.usd_save_dir}{fname}.usd"
        omni.usd.get_context().save_as_stage(save_loc, None)
        if os.path.isfile(save_loc):
            print(f"[omni.warehouse] saved .usd file to: {self.usd_save_dir}{fname}.usd")
        else:
            print(f"[omni.warehouse] .usd export FAILED: {self.usd_save_dir}{fname}.usd")


##################################################################                                     
############################# MAIN ###############################
##################################################################
if __name__ == "__main__":
    _wh_helpers = wh_helpers()
    recipes = glob.glob(f"{recipe_dir}*.txt") # gather all recipes

    for rec_loc in recipes:
        with open(rec_loc) as f: # reading the recipe from the file
            data = f.read()
        recipe = json.loads(data) # reconstructing the data as a dictionary
        
        _wh_helpers.clear_stage()
        
        # place lighting
        # for light in recipe["isaac_rect_lights"]:
        #     _wh_helpers.create_rectangular_light(light["location"], light["scale"])

        # place interior props
        for recipe_dict in [recipe["isaac_floor"], 
                            recipe["isaac_walls"], 
                            recipe["interior"], 
                            recipe["isaac_lights"]]:
            for asset in recipe_dict:
                _wh_helpers.spawn_prim(asset["filename"], 
                                       asset["location"],
                                       asset["orientation"], 
                                       asset["asset_id"], 
                                       scale=asset["scale"])

        _wh_helpers.save_stage(f"{recipe['env_type']}_{recipe['env_id']}")

    simulation_app.close() # close Isaac Sim
