import os
from pathlib import Path
import math
HOME_DIR = Path.home()
settings_path = os.path.abspath(__file__)
AutoGDM2_dir = os.path.dirname(settings_path)

# directory locations
asset_dir        = f"{HOME_DIR}/Omniverse_content/ov-industrial3dpack-01-100.1.1/" # omniverse content folder
asset_mockup_dir = f"{AutoGDM2_dir}/assets/mockup/"        # mockup folder with simple versions of assets
recipe_dir       = f"{AutoGDM2_dir}/environments/recipes/" # recipe folder
usd_scene_dir    = f"{AutoGDM2_dir}/environments/isaac_sim/" # isaac sim scenes location
geometry_dir     = f"{AutoGDM2_dir}/environments/geometry/"# geometry folder
cfd_dir          = f"{AutoGDM2_dir}/environments/cfd/"     # cfd folder
gas_data_dir     = f"{AutoGDM2_dir}/environments/gas_data/"# gas data folder
empty_ros_dir    = f"{AutoGDM2_dir}/environments/ROS/empty_project/"
gaden_env_dir    = f"{AutoGDM2_dir}/gaden_ws/src/gaden/envs/" # ROS GADEN workspace

# software locations
# omniverse assets and Isaac Sim
ISAAC_VERSION = '2022.2.0'
isaac_dir = f"{HOME_DIR}/.local/share/ov/pkg/isaac_sim-{ISAAC_VERSION}"
wh_gen_dir = f"{isaac_dir}/exts/omni.isaac.examples/omni/isaac/examples/warehouse_gen"
# blender
BLENDER_VERSION = '3.5.0'
blender_dir = f"{HOME_DIR}/Downloads/blender-{BLENDER_VERSION}-linux-x64"
# openfoam
OPENFOAM_VERSION = 'v2212'
openfoam_dir = f"{HOME_DIR}/OpenFOAM/OpenFOAM-{OPENFOAM_VERSION}"

# environment related settings
env_types  = ['wh_simple', 'wh_complex']
env_type   = env_types[0]
env_amount = 2
env_size = [10.0, 16.0, 8.0] # [X Y Z]

if env_type == 'wh_simple':
    inlet_size  = [1.2,2.4] # [Y,Z], [m]
    inlet_vel   = [1.0, 0.0, 0.0] # [X, Y,Z], [m/s]
    outlet_size = [1.5,2.4] # [Y,Z], [m]
    emptyfullrackdiv = 0.5 # least percentage of filled racks

# relevant CDF meshing settings
cfd_mesh_settings = {
    "minCellSize": 0.10, # it is recommended to keep these values uniform
    "maxCellSize": 0.10, # for easy of meshing, cfd calculation and mesh quality
    "boundaryCellSize": 0.10,
    "localRefinement": 0.0, # set to 0.0 to leave inactive
}

# relevant CFD settings
cfd_k = round(1.5 * (0.05 * math.hypot(inlet_vel[0],inlet_vel[1],inlet_vel[2]))**2,6) # turbulent kinetic energy
cfd_epsilon = round((0.09**0.75 * cfd_k**1.5)/(0.1*inlet_size[0]),6) # dissipation rate

cfd_settings = {
    "threads": len(os.sched_getaffinity(0)) - 2, # available threads for CFD is total-2 for best performance
    "endTime": 1.0,
    "writeInterval": 1.0,
    "maxCo": 2.0,
    "maxDeltaT": 0.0, # set to 0.0 to leave inactive
    "k": cfd_k,
    "epsilon": cfd_epsilon,
}

# gas dispersal settings
src_placement_types = ['random', 'specific'] # TODO implement types
src_placement = src_placement_types[0]
src_height = 2.0 # [m]

# TODO improve this implementation
# simple ( probably unnecessary ) class to store a timestep ()
class flow_field:
    def __init__(self,id):
        self.id = id

# max_num_tries = 3
# z_min = 0
#z_max = env_size_x

# asset file-locations
filenames = {
    ############################# OMNIVERSE ASSETS #############################
    # Then, we point to asset paths, to pick one at random and spawn at specific positions
    "empty_racks": f"{asset_dir}Shelves/",
    "filled_racks": f"{asset_dir}Racks/",
    "piles": f"{asset_dir}Piles/",
    "railings": f"{asset_dir}Railing/",
    # warehouse shell-specific assets (floor, walls, ceiling etc.)
    "isaac_wh_props":f"{HOME_DIR}/Omniverse_content/isaac-simple-warehouse/Props/",
    "floor": "SM_floor02.usd",
    "walls": [
        "SM_WallA_InnerCorner.usd",
        "SM_WallB_InnerCorner.usd",
        "SM_WallA_6M.usd",
        "SM_WallB_6M.usd",
    ],
    "lights":[
        "SM_LampCeilingA_04.usd", # off
        "SM_LampCeilingA_05.usd", # on
    ],
    # we can also have stand-alone assets, that are directly spawned in specific positions
    "forklift_asset": ["Forklift_A01_PR_V_NVD_01.usd"],
    "robot_asset": ["transporter.usd"],
    # We are also adding other assets from the paths above to choose from
    "empty_racks_large_asset": ["RackLargeEmpty_A1.usd", "RackLargeEmpty_A2.usd"],
    "empty_racks_long_asset": ["RackLongEmpty_A1.usd", "RackLongEmpty_A2.usd"],
    "filled_racks_large_asset": [
        "RackLarge_A1.usd",
        "RackLarge_A2.usd",
        "RackLarge_A3.usd",
        "RackLarge_A4.usd",
        "RackLarge_A5.usd",
        "RackLarge_A6.usd",
        "RackLarge_A7.usd",
        "RackLarge_A8.usd",
        "RackLarge_A9.usd",
    ],
    "filled_racks_small_asset": [
        "RackSmall_A1.usd",
        "RackSmall_A2.usd",
        "RackSmall_A3.usd",
        "RackSmall_A4.usd",
        "RackSmall_A5.usd",
        "RackSmall_A6.usd",
        "RackSmall_A7.usd",
        "RackSmall_A8.usd",
        "RackSmall_A9.usd",
    ],
    "filled_racks_long_asset": [
        "RackLong_A1.usd",
        "RackLong_A2.usd",
        "RackLong_A3.usd",
        "RackLong_A4.usd",
        "RackLong_A5.usd",
        "RackLong_A6.usd",
        "RackLong_A7.usd",
    ],
    "filled_racks_long_high_asset": ["RackLong_A8.usd", "RackLong_A9.usd"],
    "piles_asset": [
        "WarehousePile_A1.usd",
        "WarehousePile_A2.usd",
        "WarehousePile_A3.usd",
        "WarehousePile_A4.usd",
        "WarehousePile_A5.usd",
        "WarehousePile_A6.usd",
        "WarehousePile_A7.usd",
    ],
    "railings_asset": ["MetalFencing_A1.usd", "MetalFencing_A2.usd", "MetalFencing_A3.usd"],
    ############################# MOCKUP ASSETS #############################
    "empty_racks_mockup": f"{asset_mockup_dir}Shelves/",
    "filled_racks_mockup": f"{asset_mockup_dir}Racks/",
    "empty_racks_long_asset_mockup": ["RackLongEmpty_A1.obj", "RackLongEmpty_A2.obj"],
    "filled_racks_long_asset_mockup": "RackLong.obj",
}

# pairs of filelocations of assets and their corresponding mockups
file_loc_paired = {
    "filled_racks": [[filenames["filled_racks"] + filenames["filled_racks_long_asset"][0], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][1], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][2], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][3], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][4], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][5], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]],
                     [filenames["filled_racks"] + filenames["filled_racks_long_asset"][6], filenames["filled_racks_mockup"] + filenames["filled_racks_long_asset_mockup"]]],
    
    "empty_racks":  [[filenames["empty_racks"] + filenames["empty_racks_long_asset"][0], filenames["empty_racks_mockup"] + filenames["empty_racks_long_asset_mockup"][0]],
                     [filenames["empty_racks"] + filenames["empty_racks_long_asset"][1], filenames["empty_racks_mockup"] + filenames["empty_racks_long_asset_mockup"][1]]],

    "floors": [[filenames["isaac_wh_props"] + filenames["floor"], None]],

    "walls": [[filenames["isaac_wh_props"] + filenames["walls"][0], None],
              [filenames["isaac_wh_props"] + filenames["walls"][1], None],
              [filenames["isaac_wh_props"] + filenames["walls"][2], None],
              [filenames["isaac_wh_props"] + filenames["walls"][3], None],],
    
    "lights": [[filenames["isaac_wh_props"] + filenames["lights"][0], None],
               [filenames["isaac_wh_props"] + filenames["lights"][1], None]],
}