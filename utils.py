import yaml
import json
import os
import math
import csv
import zlib
from typing import Tuple
import numpy as np
from datetime import datetime
from pathlib import Path
HOME_DIR = Path.home()
main_path = os.path.abspath(__file__)
AutoGDM2_dir = os.path.dirname(main_path)

class GDMConfig:
    def __init__(self):
        self.HOME_DIR = Path.home()
        self.main_path = os.path.abspath(__file__)
        self.AutoGDM2_dir = os.path.dirname(main_path)
        self.config_dir = f'{self.AutoGDM2_dir}/config/'
        self.gdm_settings = {} # dict with all the AutoGDM settings
        self.sim_settings = {} # dict with all the Isaac Sim/Pegasus settings


    def get_current_yaml(self):
        with open(f'{self.config_dir}current.yaml', 'r') as file:
            return yaml.safe_load(file)


    def get_default_yaml(self):
        with open(f'{self.config_dir}default.yaml', 'r') as file:
            return yaml.safe_load(file)


    def set_directory_params(self, yamldict:dict) -> None:
        # directory names
        self.gdm_settings["asset_dir"]          = yamldict["directories"]["asset_dir"].format(HOME_DIR=self.HOME_DIR)
        self.gdm_settings["config_dir"]         = yamldict["directories"]["config_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["asset_mockup_dir"]   = yamldict["directories"]["asset_mockup_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["asset_custom_dir"]   = yamldict["directories"]["asset_custom_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["recipe_dir"]         = yamldict["directories"]["recipe_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["usd_scene_dir"]      = yamldict["directories"]["usd_scene_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["geometry_dir"]       = yamldict["directories"]["geometry_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["cfd_dir"]            = yamldict["directories"]["cfd_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["gas_data_dir"]       = yamldict["directories"]["gas_data_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["wind_data_dir"]      = yamldict["directories"]["wind_data_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["occ_data_dir"]       = yamldict["directories"]["occ_data_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["empty_ros_dir"]      = yamldict["directories"]["empty_ros_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)
        self.gdm_settings["gaden_env_dir"]      = yamldict["directories"]["gaden_env_dir"].format(AutoGDM2_dir=self.AutoGDM2_dir)


    def set_application_params(self, yamldict:dict) -> None:
        # applications
        self.gdm_settings["ISAAC_VERSION"]      = yamldict["software"]["isaac_sim"]["version"]
        self.gdm_settings["isaac_dir"]          = yamldict["software"]["isaac_sim"]["isaac_dir"].format(HOME_DIR=self.HOME_DIR, ISAAC_VERSION=self.gdm_settings["ISAAC_VERSION"])
        self.gdm_settings["wh_gen_dir"]         = yamldict["software"]["isaac_sim"]["wh_gen_dir"].format(isaac_dir=self.gdm_settings["isaac_dir"])
        self.gdm_settings["BLENDER_VERSION"]    = yamldict["software"]["blender"]["version"]
        self.gdm_settings["blender_dir"]        = yamldict["software"]["blender"]["blender_dir"].format(HOME_DIR=self.HOME_DIR, BLENDER_VERSION=self.gdm_settings["BLENDER_VERSION"])
        self.gdm_settings["OPENFOAM_VERSION"]   = yamldict["software"]["openfoam"]["version"]
        self.gdm_settings["openfoam_dir"]       = yamldict["software"]["openfoam"]["openfoam_dir"].format(HOME_DIR=self.HOME_DIR, OPENFOAM_VERSION=self.gdm_settings["OPENFOAM_VERSION"])


    def set_environment_params(self, yamldict:dict) -> None:
        # environment(s)
        self.gdm_settings["env_types"]  = yamldict["environment"]["env_types"]
        self.gdm_settings["env_type"]   = self.gdm_settings["env_types"][yamldict["environment"]["env_type"]]
        self.gdm_settings["env_amount"] = yamldict["environment"]["env_amount"]
        self.gdm_settings["env_size"]   = yamldict["environment"]["env_size"]
        self.gdm_settings["env_list"]   = [f"{self.gdm_settings['env_type']}_{str(i).zfill(4)}" for i in range(self.gdm_settings['env_amount'])]

        # if self.gdm_settings["env_type"] == 'wh_empty' or self.gdm_settings["env_type"] == 'wh_simple':
        self.gdm_settings["inlet_size"]         = yamldict["env_wh"]["inlet_size"]
        self.gdm_settings["inlet_vel"]          = yamldict["env_wh"]["inlet_vel"]
        self.gdm_settings["outlet_size"]        = yamldict["env_wh"]["outlet_size"]
        self.gdm_settings["emptyfullrackdiv"]   = yamldict["env_wh"]["emptyfullrackdiv"]
        self.gdm_settings["white_walls"]        = yamldict["env_wh"]["white_walls"]


    def set_cfd_params(self,yamldict:dict) -> None:
        # cfd mesh settings
        self.gdm_settings["cfd_mesh_settings"] = {
            "minCellSize":      yamldict["cfd"]["mesh"]["minCellSize"], 
            "maxCellSize":      yamldict["cfd"]["mesh"]["maxCellSize"], 
            "boundaryCellSize": yamldict["cfd"]["mesh"]["boundaryCellSize"],
            "localRefinement":  yamldict["cfd"]["mesh"]["localRefinement"], 
        }

        # threads used for solving
        if yamldict["cfd"]["solving"]["threads"] == 0:
            threads = len(os.sched_getaffinity(0)) - 2
        else:
            threads = yamldict["cfd"]["solving"]["threads"]

        # relevant cfd solver settings
        cfd_k = round(1.5 * (0.05 * math.hypot(self.gdm_settings["inlet_vel"][0],self.gdm_settings["inlet_vel"][1],self.gdm_settings["inlet_vel"][2]))**2,6) # turbulent kinetic energy
        cfd_epsilon = round((0.09**0.75 * cfd_k**1.5)/(0.1*self.gdm_settings["inlet_size"][0]),6) # dissipation rate

        self.gdm_settings["cfd_settings"] = {
            "threads":          threads,
            "endTime":          yamldict["cfd"]["solving"]["endTime"], 
            "writeInterval":    yamldict["cfd"]["solving"]["writeInterval"],
            "maxCo":            yamldict["cfd"]["solving"]["maxCo"],
            "maxDeltaT":        yamldict["cfd"]["solving"]["maxDeltaT"], 
            "nOuterCorrectors": yamldict["cfd"]["solving"]["nOuterCorrectors"], 
            "k":                cfd_k,
            "epsilon":          cfd_epsilon,
            "latestTime":       yamldict["cfd"]["solving"]["latestTime"],
            "timeRange":        yamldict["cfd"]["solving"]["timeRange"]
        }

    def set_gas_dispersal_params(self, yamldict:dict) -> None:
        # gas dispersal settings
        self.gdm_settings["src_placement_types"] = yamldict["gas_dispersal"]["src_placement_types"]
        self.gdm_settings["src_placement_type"]  = self.gdm_settings["src_placement_types"][yamldict["gas_dispersal"]["src_placement_type"]]
        self.gdm_settings["src_placement"]       = yamldict["gas_dispersal"]["src_placement"] # TODO: add if statement for random settings
        self.gdm_settings["gas_type"]            = yamldict["gas_dispersal"]["gas_type"]
        self.gdm_settings["sim_time"]            = yamldict["gas_dispersal"]["sim_time"]
        self.gdm_settings["time_step"]           = yamldict["gas_dispersal"]["time_step"]
        self.gdm_settings["wind_looping"]        = yamldict["gas_dispersal"]["wind_looping"]
        self.gdm_settings["wind_start_step"]     = yamldict["gas_dispersal"]["wind_start_step"]
        self.gdm_settings["wind_stop_step"]      = yamldict["gas_dispersal"]["wind_stop_step"]

    def set_asset_params(self, yamldict: dict) -> None:
        # assets
        assets = yamldict["assets"]
        # 'repair' the 'f-strings'
        assets["empty_racks"]       = assets["empty_racks"].format(asset_dir=self.gdm_settings["asset_dir"])
        assets["filled_racks"]      = assets["filled_racks"].format(asset_dir=self.gdm_settings["asset_dir"])
        assets["piles"]             = assets["piles"].format(asset_dir=self.gdm_settings["asset_dir"])
        assets["railings"]          = assets["railings"].format(asset_dir=self.gdm_settings["asset_dir"])
        assets["isaac_wh_props"]    = assets["isaac_wh_props"].format(HOME_DIR=self.HOME_DIR)
        assets["isaac_custom"]      = assets["isaac_custom"].format(asset_custom_dir=self.gdm_settings["asset_custom_dir"])
        assets["forklift"]          = assets["forklift_asset"].format(HOME_DIR=self.HOME_DIR)
        assets["empty_racks_mockup"] = assets["empty_racks_mockup"].format(asset_mockup_dir=self.gdm_settings["asset_mockup_dir"])
        assets["filled_racks_mockup"] = assets["filled_racks_mockup"].format(asset_mockup_dir=self.gdm_settings["asset_mockup_dir"])
        assets["forklift_mockup"]   = assets["forklift_mockup"].format(asset_mockup_dir=self.gdm_settings["asset_mockup_dir"])
        assets["piles_mockup"]      = assets["piles_mockup"].format(asset_mockup_dir=self.gdm_settings["asset_mockup_dir"])
        
        self.gdm_settings["assets"] = assets

        # pairs of filelocations of assets and their corresponding mockups
        self.gdm_settings["file_loc_paired"] = {
            "filled_racks": [[assets["filled_racks"] + assets["filled_racks_long_asset"][0], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][1], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][2], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][3], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][4], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][5], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]],
                             [assets["filled_racks"] + assets["filled_racks_long_asset"][6], assets["filled_racks_mockup"] + assets["filled_racks_long_asset_mockup"]]],
            
            "empty_racks":  [[assets["empty_racks"] + assets["empty_racks_long_asset"][0], assets["empty_racks_mockup"] + assets["empty_racks_long_asset_mockup"][0]],
                             [assets["empty_racks"] + assets["empty_racks_long_asset"][1], assets["empty_racks_mockup"] + assets["empty_racks_long_asset_mockup"][1]]],

            "piles": [[assets["piles"] + assets["piles_asset"][3], assets["piles_mockup"] + assets["piles_asset_mockup"][0]],  # WarehousePile_A4
                      [assets["piles"] + assets["piles_asset"][4], assets["piles_mockup"] + assets["piles_asset_mockup"][1]],  # WarehousePile_A5
                      [assets["piles"] + assets["piles_asset"][6], assets["piles_mockup"] + assets["piles_asset_mockup"][2]]], # WarehousePile_A7
            
            "floors": [[assets["isaac_wh_props"] + assets["floor"], None]],

            "walls": [[assets["isaac_wh_props"] + assets["walls"][0], None],
                      [assets["isaac_wh_props"] + assets["walls"][1], None],
                      [assets["isaac_wh_props"] + assets["walls"][2], None],
                      [assets["isaac_wh_props"] + assets["walls"][3], None],],
            
            "lights": [[assets["isaac_wh_props"] + assets["lights"][0], None],
                       [assets["isaac_custom"] + assets["lights"][1], None]],

            "forklift": [[assets["forklift"], assets["forklift_mockup"] + assets["forklift_asset_mockup"]]],
        }


    def pretty(self, conf:dict) -> str:
        return json.dumps(conf, indent=2)


    def save_gdm_settings(self, comment:str='') -> None:
        if comment:
            filename = f'{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().strftime("%H:%M:%S")}_{comment}'
        else:
            filename = f'{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().strftime("%H:%M:%S")}'
        
        with open(f'{self.config_dir}{filename}.yaml', 'w') as file:
            yaml.dump(self.gdm_settings, file)
            file.close()


    def set_gdm_params(self, yamldict:dict) -> None:
        self.set_directory_params(yamldict)
        self.set_application_params(yamldict)
        self.set_environment_params(yamldict)
        self.set_cfd_params(yamldict)
        self.set_gas_dispersal_params(yamldict)
        self.set_asset_params(yamldict)


    def current_gdm_settings(self) -> dict:
        yamldict = self.get_current_yaml()
        self.set_gdm_params(yamldict)
        self.save_gdm_settings(yamldict["comment"])
        
        return self.gdm_settings


    def default_gdm_settings(self) -> dict:
        yamldict = self.get_default_yaml()
        self.set_gdm_params(yamldict)
        self.save_gdm_settings(yamldict["comment"])
        
        return self.gdm_settings


# TODO improve this implementation
# simple ( probably unnecessary ) class to store a timestep ()
class flow_field:
    def __init__(self,id):
        self.id = id


def is_float(element:any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


# reads compressed gas data
def read_gas_data(file_path) -> Tuple[np.ndarray,np.ndarray]:
    with open(file_path, 'rb') as file:
        compressed_data = file.read()

    # first decompress the file
    decompressed_data = zlib.decompress(compressed_data)

    # header datatype
    header_dtype = np.dtype([('h', np.uint32),
                            ('env_min_x', np.float64),
                            ('env_min_y', np.float64),
                            ('env_min_z', np.float64),
                            ('env_max_x', np.float64),
                            ('env_max_y', np.float64),
                            ('env_max_z', np.float64),
                            ('env_cells_x', np.uint32),
                            ('env_cells_y', np.uint32),
                            ('env_cells_z', np.uint32),
                            ('cell_size_x', np.float64),
                            ('cell_size_y', np.float64),
                            ('cell_size_z', np.float64),
                            ('gas_source_pos_x', np.float64),
                            ('gas_source_pos_y', np.float64),
                            ('gas_source_pos_z', np.float64),
                            ('gas_type', np.uint32),
                            ('filament_num_moles_of_gas', np.float64),
                            ('num_moles_all_gases_in_cm3', np.float64),
                            ('binary_bool', np.uint32)])

    # filament datatype
    filament_dtype = np.dtype([('id', np.uint32),
                            ('pose_x', np.float64),
                            ('pose_y', np.float64),
                            ('pose_z', np.float64),
                            ('sigma', np.float64)])

    # TODO - combine all gas iterations into one array for a potential speed increase
    # read data from buffer
    filament_header = np.frombuffer(decompressed_data, dtype=header_dtype, count=1)
    filament_data = np.frombuffer(decompressed_data, dtype=filament_dtype, 
                                offset=header_dtype.itemsize)

    # return the extracted data
    return filament_header, filament_data


def read_wind_data(file_paths) -> np.ndarray:
    windfields_lst = []
    
    # read files and put into list
    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            data = file.read()

        UVW = np.split(np.frombuffer(data, dtype=np.float64), 3)

        wind_vectors = np.zeros((np.shape(UVW)[1],3))
        wind_vectors[:,0] = UVW[0]
        wind_vectors[:,1] = UVW[1]
        wind_vectors[:,2] = UVW[2]

        windfields_lst.append(wind_vectors)

    windfields_arr = np.zeros((len(file_paths), np.shape(windfields_lst[0])[0], 3))
    
    # puts lists into one array
    for i, windfield in enumerate(windfields_lst):
        windfields_arr[i] = windfield
        
    # return the extracted data
    return windfields_arr


def read_occ_csv(filepath) -> Tuple[dict,np.ndarray]:
    header = {}
    
    with open(filepath, 'r') as csv_file:
        csv_lst = list(csv.reader(csv_file))

        # extract header info
        header['env_min'] = [float(j) for j in csv_lst[0][0].split(" ")[1:]]
        header['env_max'] = [float(j) for j in csv_lst[1][0].split(" ")[1:]]
        header['num_cells'] = [int(j) for j in csv_lst[2][0].split(" ")[1:]]
        header['cell_size'] = float(csv_lst[3][0].split(" ")[1:][0])

        occ_arr = np.zeros((header['num_cells'][2],
                            header['num_cells'][0],
                            header['num_cells'][1]), dtype=int)

        for z_it in range(header['num_cells'][2]):
            x_it = 0
            while True:    
                row = csv_lst[(4 + z_it*(header['num_cells'][0]+1)) + x_it][0]
                if row == ';':
                    break
                occ_arr[z_it,x_it,:] = [int(j) for j in row.split(" ")[:-1]]
                x_it += 1

    return header, occ_arr
