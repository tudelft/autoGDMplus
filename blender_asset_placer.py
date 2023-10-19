### blender_asset_placer.py
### imports recipe dict and exports scene
###   H. Erwich
###  23-05-2023
import sys # get recipe and mockup scene dir
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all the args after " -- "
recipe_dir = argv[0]    # recipe folder
geometry_dir = argv[1]  # blender export folder

import bpy
import os
import glob
import json
import random
import numpy as np

class Utils:
    # Useful utilities and shortcuts
    def __init__(self):
        self.blend_file_path = bpy.data.filepath
        self.directory = os.path.dirname(self.blend_file_path)

    def get_asset_name(self, path_str):
        asset_name = path_str.rsplit('/', 1)[-1][:-4] #returns object name, [:-4] to remove .usd/.obj
        return asset_name

    def usd_import(self, filepath, scale=0.01):
        bpy.ops.wm.usd_import(filepath=filepath, scale=scale) #import .usd file, scale set for correct import

    def set_active_ob(self, asset_str):
        ob = bpy.context.scene.objects[asset_str]    # Get the object
        bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
        bpy.context.view_layer.objects.active = ob   # Make the object the active object 
        ob.select_set(True)                          # Select the object
  
    def delete_all(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
   
    def get_ob_dimensions(self):
        return bpy.context.object.dimensions

    def obj_import(self, filepath):
        bpy.ops.wm.obj_import(filepath=filepath)
   
    def obj_export(self, filename):
        target_file = os.path.join(self.directory, str(filename))
        bpy.ops.export_scene.obj(filepath=target_file,
                                 check_existing=False,
                                 axis_forward='Y', axis_up='Z') # orientation set to match the axis system in paraview

    def stl_export(self, filename, selection=False, text=True):
        target_file = os.path.join(self.directory, str(filename))
        bpy.ops.export_mesh.stl(filepath=target_file,
                                check_existing=False,
                                use_selection=selection,
                                ascii=text, # required to combine them with the cat command
                                axis_forward='Y', axis_up='Z')
                             
    def place_boundary_cube(self, scale):
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', 
                                        location=(0.5*scale[0], 0.5*scale[1], 0.5*scale[2]), 
                                        scale=(0.5*scale[0], 0.5*scale[1], 0.5*scale[2]))

    def translate(self, position):
        bpy.ops.transform.translate(value=(position[0], position[1], position[2]), 
                                    orient_axis_ortho='X', 
                                    orient_type='GLOBAL', 
                                    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                    orient_matrix_type='GLOBAL', 
                                    constraint_axis=(True, True, False), 
                                    mirror=False, use_proportional_edit=False, 
                                    proportional_edit_falloff='SMOOTH', 
                                    proportional_size=1, 
                                    use_proportional_connected=False, 
                                    use_proportional_projected=False, 
                                    snap=False, 
                                    snap_elements={'INCREMENT'}, 
                                    use_snap_project=False, 
                                    snap_target='CLOSEST', 
                                    use_snap_self=True, 
                                    use_snap_edit=True, 
                                    use_snap_nonedit=True, 
                                    use_snap_selectable=False, 
                                    release_confirm=True)
    
    def rotate(self, degrees):
        bpy.context.active_object.rotation_euler[0] = np.radians(degrees[0])
        bpy.context.active_object.rotation_euler[1] = np.radians(degrees[1])
        bpy.context.active_object.rotation_euler[2] = np.radians(degrees[2])

    def rotate2(self, degrees):
        bpy.ops.transform.rotate(value=np.radians(degrees[0]), orient_axis='X') # TODO: check if other axis also need sign change
        bpy.ops.transform.rotate(value=np.radians(degrees[1]), orient_axis='Y')
        bpy.ops.transform.rotate(value=np.radians(-degrees[2]), orient_axis='Z') # minus to match transform function function in isaac sim

    def scale(self, scale):
        bpy.context.active_object.scale[0] = 0.5*scale[0]
        bpy.context.active_object.scale[1] = 0.5*scale[1]
        bpy.context.active_object.scale[2] = 0.5*scale[2]
    
    # def apply_modifiers(obj):
    #     ctx = bpy.context.copy()
    #     ctx['object'] = obj
    #     for _, m in enumerate(obj.modifiers):
    #         try:
    #             ctx['modifier'] = m
    #             bpy.ops.object.modifier_apply(ctx, modifier=m.name)
    #         except RuntimeError:
    #             print(f"Error applying {m.name} to {obj.name}, removing it instead.")
    #             obj.modifiers.remove(m)

    #     for m in obj.modifiers:
    #         obj.modifiers.remove(m)

                     
##################################################################                                     
############################# MAIN ###############################
##################################################################
u = Utils()
u.delete_all() # deletes default objects in the scene
recipes = glob.glob(f"{recipe_dir}*.txt") # gather all recipes

# build each recipe
for rec_loc in recipes:
    u.delete_all()
    # reading the recipe from the file
    with open(rec_loc) as f:
        data = f.read()
    recipe = json.loads(data) # reconstructing the data as a dictionary

    # create mesh geometry and gaden geometry directory if it does not exist already
    mesh_dir = f"{geometry_dir}{recipe['env_type']}_{recipe['env_id']}/mesh/"
    gaden_dir = f"{geometry_dir}{recipe['env_type']}_{recipe['env_id']}/gaden/"
    os.makedirs(mesh_dir, exist_ok=True)
    os.makedirs(gaden_dir, exist_ok=True)

    # place boundaries and export
    for plane in recipe["sides"]:
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        for obj in bpy.context.selected_objects: # rename object with asset id
            obj.name = plane["asset_id"]        
        u.scale(plane["dimensions"])
        u.rotate(plane["orientation"])
        u.translate(plane["location"])

    u.stl_export(f"{mesh_dir}/sides.stl")

    # place inlet and export
    u.delete_all()
    for plane in recipe["inlets"]:
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        for obj in bpy.context.selected_objects: # rename object with asset id
            obj.name = plane["asset_id"]        
        u.scale(plane["dimensions"])
        u.rotate(plane["orientation"])
        u.translate(plane["location"])

    u.stl_export(f"{mesh_dir}/inlet.stl")

    # place outlet and export
    u.delete_all()
    for plane in recipe["outlets"]:
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        for obj in bpy.context.selected_objects: # rename object with asset id
            obj.name = plane["asset_id"]        
        u.scale(plane["dimensions"])
        u.rotate(plane["orientation"])
        u.translate(plane["location"])

    u.stl_export(f"{mesh_dir}/outlet.stl")

    # place interior and export
    u.delete_all()
    for asset in recipe["interior"]:
        u.obj_import(asset["mockup_file"])
        for obj in bpy.context.selected_objects: # rename object with asset id
            obj.name = asset["asset_id"]
        u.rotate2(asset["orientation"])
        u.translate(asset["location"]) # translate object to specified location#

    u.stl_export(f"{mesh_dir}/interior.stl")
    u.stl_export(f"{gaden_dir}/interior_ascii.stl")
    u.stl_export(f"{gaden_dir}/interior_binary.stl",text=False)

    # gaden only geometry
    u.delete_all()
    for cube in recipe["gaden_geom"]:
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        for obj in bpy.context.selected_objects: # rename object with asset id
            obj.name = cube["asset_id"]      
        u.scale(cube["dimensions"])
        u.rotate(cube["orientation"])
        u.translate(cube["location"])
        if 'wall' not in cube["asset_id"]:
            u.stl_export(f"{gaden_dir}/{cube['asset_id']}_ascii.stl",selection=True)
            u.stl_export(f"{gaden_dir}/{cube['asset_id']}_binary.stl",selection=True, text=False)
        elif 'inside' not in cube["asset_id"]: #TODO inside is still being exported?
            u.stl_export(f"{gaden_dir}/{cube['asset_id']}_ascii.stl",selection=True)
            u.stl_export(f"{gaden_dir}/{cube['asset_id']}_binary.stl",selection=True, text=False)

    # gaden boolean operations
    objects = bpy.data.objects

    for i,booldict in enumerate(recipe["gaden_bools"]):
        #bool_op = objects['walls'].modifiers.new(type="BOOLEAN", name=f"bool_{i}")
        bool_op = objects[booldict[0]["asset_id"]].modifiers.new(type="BOOLEAN", name=f"bool_{i}")
        bool_op.object = objects[str(booldict[1]["asset_id"])]
        bool_op.operation = booldict[2]

    u.set_active_ob('walls')
    u.stl_export(f"{gaden_dir}/walls_ascii.stl",selection=True)
    u.stl_export(f"{gaden_dir}/walls_binary.stl",selection=True, text=False)

u.delete_all()
