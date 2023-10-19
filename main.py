import os
import re
import json
import glob
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from colorama import Fore, Back, Style
from layout_gen import generate_recipes
from utils import GDMConfig, flow_field, is_float, read_gas_data, read_wind_data, read_occ_csv

HOME_DIR = Path.home()
main_path = os.path.abspath(__file__)
AutoGDM2_dir = os.path.dirname(main_path)

class AutoGDM2:
    def __init__(self, settings:dict):
        self.settings = settings
        self.isaac_dir = self.settings["isaac_dir"]
        self.wh_gen_dir = self.settings["wh_gen_dir"]
        self.blender_dir = self.settings["blender_dir"]
        self.env_lst = self.settings["env_list"]
        self.env_lst_failed = []


    # different color and formatting to display the terminal
    def printGDMStyle(self, string):
        print(Fore.GREEN + Style.BRIGHT + string)
        print(Style.RESET_ALL)


    # get list of environment names
    def get_envs(self) -> None:
        return os.listdir(self.settings["geometry_dir"])
    

    def remove_envs(self, indexes:list) -> None:
        for index in sorted(indexes, reverse=True):
            self.env_lst_failed.append(self.env_lst[index])
            del self.env_lst[index]


    # cleanup func the AutoGDM2 directories
    def cleanup(self) -> None:
        self.printGDMStyle("[AutoGDM2] Performing cleanup...")

        # remove everything in ./environments/recipes
        if os.listdir(self.settings["recipe_dir"]):
            os.system(f"cd {self.settings['recipe_dir']} && rm -v *")
        else:
            self.printGDMStyle("[AutoGDM2] No recipies to clean.")

        # remove everything in ./environments/geometry
        if os.listdir(self.settings["geometry_dir"]):
            os.system(f"cd {self.settings['geometry_dir']} && rm -rv *")
        else:
            self.printGDMStyle("[AutoGDM2] No mockup scenes to clean.")
        
        # remove everything in ./environments/isaac_sim
        if os.listdir(self.settings["usd_scene_dir"]):
            os.system(f"cd {self.settings['usd_scene_dir']} && rm -v *")
        else:
            self.printGDMStyle("[AutoGDM2] No usd scenes to clean.")

        # remove everything in ./environments/cfd EXCEPT the 'default_cfd_case' directory
        rm_string = ' '.join([str(item) for item in [x for x in os.listdir(self.settings["cfd_dir"]) if 'default' not in x]])
        if rm_string:
            os.system(f"cd {self.settings['cfd_dir']} && rm -rv {rm_string}")
        else:
            self.printGDMStyle("[AutoGDM2] No CFD cases to clean.")
        
        # remove all directories in gaden_env_dir (NOT CMakelLists.txt and package.xml)
        if os.listdir(self.settings["gaden_env_dir"]):
            os.system(f"cd {self.settings['gaden_env_dir']} && rm -rv */")
        else:
            self.printGDMStyle("[AutoGDM2] No usd scenes to clean.")

        # remove everything in ./environments/gas_data
        if os.listdir(self.settings["gas_data_dir"]):
            os.system(f"cd {self.settings['gas_data_dir']} && rm -rv *")
        else:
            self.printGDMStyle("[AutoGDM2] No gas data to clean.")

        # remove everything in ./environments/wind_data
        if os.listdir(self.settings["wind_data_dir"]):
            os.system(f"cd {self.settings['wind_data_dir']} && rm -rv *")
        else:
            self.printGDMStyle("[AutoGDM2] No wind data to clean.")

        # remove everything in ./environments/occupancy
        if os.listdir(self.settings["occ_data_dir"]):
            os.system(f"cd {self.settings['occ_data_dir']} && rm -rv *")
        else:
            self.printGDMStyle("[AutoGDM2] No occupancy data to clean.")

        self.printGDMStyle("[AutoGDM2] Cleanup completed.")


    # layout generator, results in recipes.txt 
    def layout_gen(self): 
        self.printGDMStyle(f"[AutoGDM2] Generating {self.settings['env_amount']} recipes for type {self.settings['env_type']}...")
        generate_recipes(self.settings)
        self.printGDMStyle("[AutoGDM2] Completed environment recipe generation. ")


    # blender .stl generator, results in stls in environments/mockup_scenes
    def blender_asset_placer(self): 
        self.printGDMStyle("[AutoGDM2] Creating .stl files...")
        blender_exe = os.path.join(self.blender_dir, 'blender')
        command = f"{blender_exe} --background --python blender_asset_placer.py -- {self.settings['recipe_dir']} {self.settings['geometry_dir']}" # run blender in the background
        os.system(command)
        self.printGDMStyle("[AutoGDM2] Completed .stl file creation.")        


    # isaac usd scene generator, results in usd scenes in environments/isaac_sim
    def isaac_asset_placer(self): 
        self.printGDMStyle("[AutoGDM2] Creating .usd scenes...")
        isaac_exe = os.path.join(self.isaac_dir, 'python.sh')
        wh_gen_exe= os.path.join(self.wh_gen_dir, 'isaac_asset_placer.py')
        command = f"{isaac_exe} {wh_gen_exe} -- {self.settings['recipe_dir']} {self.settings['usd_scene_dir']}"
        os.system(command)
        self.printGDMStyle("[AutoGDM2] Completed .usd scene creation.")  


    # run cfMesh for created .stl files
    def cfd_mesh(self):
        self.printGDMStyle("[AutoGDM2] Creating CFD meshes...")

        for scenedir in self.env_lst:
            currentdir = f"{self.settings['geometry_dir']}{scenedir}/mesh/"
            self.printGDMStyle(f"[AutoGDM2] Meshing environment {scenedir}...")

            # remove comined.stl if it already exists
            if os.path.isfile(f"{currentdir}combined.stl"): os.remove(f"{currentdir}combined.stl")

            stls = glob.glob(f"{currentdir}*.stl")            # gather all stls
            stls_str = ' '.join([str(item) for item in stls]) # put them in one string separated by spaces

            # edit the solid name at the start and end of each .stl file
            # (bad method for large files but it works for now)
            for stl_path in stls:
                with open(f"{stl_path}", "r") as f:
                    stl_name = stl_path.rsplit('/', 1)[-1][:-4]
                    data = f.readlines()
                    data[0]  = f"solid {stl_name}\n" # don't forget to add a newline!
                    data[-1] = f"endsolid {stl_name}\n"

                with open(f"{stl_path}", "w") as f: 
                    f.writelines(data)
                    f.close()

            # combine .stls with cat command and change to a .fms file
            catcommand = f"cat {stls_str} >> combined.stl"
            fmscommand = "surfaceFeatureEdges combined.stl combined.fms"
            os.system(f"cd {currentdir} && {catcommand} && {fmscommand}")

            # change boundary conditions at the start of combined.fms
            with open(f"{currentdir}combined.fms", "r") as f:
                data = f.readlines()
                for i,line in enumerate(data[0:20]): # check only the first 20 lines
                    if "outlet" in line: data[i] = "outlet patch\n"
                    elif "interior" in line: data[i] = "interior wall\n"
                    elif "inlet" in line: data[i] = "inlet patch\n"
                    elif "sides" in line: data[i] = "sides wall\n"

            with open(f"{currentdir}combined.fms", "w") as f:
                f.writelines(data)
                f.close()

            # create cfd case directory if it does not exist already from defualt_cfd_case
            cfd_case_dir = f"{self.settings['cfd_dir']}{scenedir}/"
            if not os.path.isdir(cfd_case_dir):
                os.system(f"cp -r {self.settings['cfd_dir']}default_cfd_case {cfd_case_dir}")

            # move .fms to separate cfd dir in environments/cfd
            os.system(f"cp {currentdir}combined.fms {cfd_case_dir}")

            # set mesh settings
            with open(f"{cfd_case_dir}system/meshDict", "r") as f:
                data = f.readlines()
                data[20] = f"minCellSize {self.settings['cfd_mesh_settings']['minCellSize']};\n"
                data[22] = f"maxCellSize {self.settings['cfd_mesh_settings']['maxCellSize']};\n"
                data[24] = f"boundaryCellSize {self.settings['cfd_mesh_settings']['boundaryCellSize']};\n"
                if self.settings['cfd_mesh_settings']["localRefinement"] != 0:
                    data[26] = "localRefinement\n" # uncomment localRefinement setting
                    data[30] = f"        cellSize {self.settings['cfd_mesh_settings']['localRefinement']};\n"
                    data[32] = "}\n"

            with open(f"{cfd_case_dir}/system/meshDict", "w") as f:
                f.writelines(data)
                f.close()

            # run the meshing process
            os.system(f"cd {cfd_case_dir} && cartesianMesh")

        self.printGDMStyle("[AutoGDM2] Completed CFD mesh creation.")


    def cfd_set_params(self):
        self.printGDMStyle("[AutoGDM2] Setting CFD parameters...")

        for cfd_case in self.env_lst:
            cfd_case_dir = f"{self.settings['cfd_dir']}{cfd_case}/"

            #### 0 folder ####
            # set U
            with open(f"{cfd_case_dir}0/U", "r") as f:
                data = f.readlines()
                data[25] = f"        value           uniform ({self.settings['inlet_vel'][0]} {self.settings['inlet_vel'][1]} {self.settings['inlet_vel'][2]});\n"

            with open(f"{cfd_case_dir}0/U", "w") as f:
                f.writelines(data)
                f.close()

            # set k (turbelent kinetic energy)
            with open(f"{cfd_case_dir}0/k", "r") as f:
                data = f.readlines()
                data[21] = f"internalField   uniform {self.settings['cfd_settings']['k']};\n"
                for i in [28, 39, 45]:
                    data[i] = f"        value           uniform {self.settings['cfd_settings']['k']};\n"

            with open(f"{cfd_case_dir}0/k", "w") as f:
                f.writelines(data)
                f.close()

            # set epsilon (dissipation rate)
            with open(f"{cfd_case_dir}0/epsilon", "r") as f:
                data = f.readlines()
                data[21] = f"internalField   uniform {self.settings['cfd_settings']['epsilon']};\n"
                for i in [28, 39, 45]:
                    data[i] = f"        value           uniform {self.settings['cfd_settings']['epsilon']};\n"

            with open(f"{cfd_case_dir}0/epsilon", "w") as f:
                f.writelines(data)
                f.close

            #### sytem folder ####
            # decomposeParDict (set the division of the mesh to the amount of threads)
            with open(f"{cfd_case_dir}system/decomposeParDict", "r") as f:
                data = f.readlines()
                data[17] = f"numberOfSubdomains  {self.settings['cfd_settings']['threads']};\n"

            with open(f"{cfd_case_dir}system/decomposeParDict", "w") as f:
                f.writelines(data)
                f.close()

            # controlDict
            with open(f"{cfd_case_dir}system/controlDict", "r") as f:
                data = f.readlines()
                data[24] = f"endTime         {self.settings['cfd_settings']['endTime']};\n"
                data[30] = f"writeInterval   {self.settings['cfd_settings']['writeInterval']};\n"
                data[48] = f"maxCo           {self.settings['cfd_settings']['maxCo']};\n"
                if self.settings['cfd_settings']['maxDeltaT'] != 0.0:
                    data[50] = f"maxDeltaT 	{self.settings['cfd_settings']['maxDeltaT']};\n"

            with open(f"{cfd_case_dir}system/controlDict", "w") as f:
                f.writelines(data)
                f.close()

            # fvSolution
            with open(f"{cfd_case_dir}system/fvSolution", "r") as f:
                data = f.readlines()
                data[51] = f"    nOuterCorrectors		{self.settings['cfd_settings']['nOuterCorrectors']};\n"

            with open(f"{cfd_case_dir}system/fvSolution", "w") as f:
                f.writelines(data)
                f.close()

        self.printGDMStyle("[AutoGDM2] CFD parameters set.")


    def cfd_run(self):
        self.printGDMStyle("[AutoGDM2] Running CFD...")

        for cfd_case in self.env_lst:
            cfd_case_dir = f"{self.settings['cfd_dir']}{cfd_case}/"
            self.printGDMStyle(f"[AutoGDM2] Running CFD for case {cfd_case}...")
            runcmd = f"mpirun --use-hwthread-cpus -np {self.settings['cfd_settings']['threads']} pimpleFoam -parallel"

            if self.settings['cfd_settings']['latestTime']:
                processcmd = f"postProcess -func 'components(U)' -latestTime && postProcess -func 'writeCellCentres' -latestTime"
            else:
                processcmd = f"postProcess -func 'components(U)' -time {self.settings['cfd_settings']['timeRange']} && postProcess -func 'writeCellCentres' -time {self.settings['cfd_settings']['timeRange']}"            
            
            # decompose -> run CFD -> reconstruct -> postprocess
            os.system(f"cd {cfd_case_dir} && decomposePar && {runcmd} && reconstructPar && {processcmd}")

        self.printGDMStyle("[AutoGDM2] Completed CFD.")
        return


    def make_ros_folder(self): # adapted from AUTOGDM TODO: improve
        self.printGDMStyle(f"[AutoGDM2] Creating ROS directories in {self.settings['gaden_env_dir']}...")
        
        for env in self.env_lst:
            self.ros_loc = f"{self.settings['gaden_env_dir']}{env}"
            if os.path.exists(self.ros_loc):
                os.system(f"rm -rf {self.ros_loc}") # TODO move to cleanup?

            os.system(f"mkdir -p {self.ros_loc}") # create env dir in gaden_env_dir
            os.system(f"cp -r {self.settings['empty_ros_dir']}* {self.ros_loc}") # copy the empty ROS dir to it        
        
        self.printGDMStyle(f"[AutoGDM2] Created ROS directories in {self.settings['gaden_env_dir']}.")


    # prepare ROS directory with environment-specific configurations (adapted from AutoGDM)
    def prep_ros(self):
        self.printGDMStyle(f"[AutoGDM2] Preparing ROS...")
        sim_arg = f"{int(sum(self.settings['inlet_vel']))}ms" # simulation argument (required in GADEN.launch, gives possibility to use multiple wind simulations)
        invalid_idx = []

        for env_idx,env in enumerate(self.env_lst):

            self.cfd_folder = f"{self.settings['cfd_dir']}{env}"
            self.ros_loc = f"{self.settings['gaden_env_dir']}{env}"
            os.system(f"mkdir -p {self.ros_loc}/wind_simulations/{sim_arg}/") # create dir for specific wind simulation
            
            time_dirs = [i for i in os.listdir(self.cfd_folder) if is_float(i)]
            time_dirs_float = [float(i) for i in time_dirs] # necessary for np.argmax
            
            if self.settings['cfd_settings']['latestTime']:
                steps = [time_dirs[np.argmax(time_dirs_float)]]
            else:
                # get start and stop value from settings
                start_stop = [float(i) for i in re.findall(r"[-+]?\d*\.?\d+",self.settings['cfd_settings']['timeRange'])]
                # get all timesteps that are within the range
                steps = np.sort([i for i in time_dirs_float if i >= start_stop[0] and i <= start_stop[1]])
                steps = [str(i) for i in steps]
                # change float values to integer if possible
                for i,step in enumerate(steps):
                    if float(steps[i]).is_integer():
                        steps[i] = str(int(float(step))) # ugly but it works!
            
            for step_idx,step in enumerate(steps):
                try:
                    f = open(f"{self.cfd_folder}/{step}/C")
                except FileNotFoundError:
                    print(f"CFD failed for this environment, skipping...")
                    invalid_idx.append(env_idx) # save invalid env idx to remove later
                    continue
                
                print(f"Preparing windfield {step_idx + 1}/{len(steps)}")
                
                self.points_file = f.readlines() 
                self.points_x = []
                self.points_y = []
                self.points_z = []

                for i,line in enumerate(self.points_file):
                    if i >=23:
                        if line.find(")") == 0:
                            break
                        
                        line = line.replace("("," ").replace(")"," ").split()
                        self.points_x.append(float(line[0]))
                        self.points_y.append(float(line[1]))
                        self.points_z.append(float(line[2]))
                
                    
                timestep = flow_field(step)
                f = open(self.cfd_folder+"/"+str(step)+'/U')
                flow_data = f.readlines()    
                Ux = []
                Uy = []
                Uz = []

                for i,line in enumerate(flow_data):
                    if i >=23:
                        if line.find(")") == 0:
                            break
                        
                        line = line.replace("("," ").replace(")"," ").split()
                        Ux.append(float(line[0]))
                        Uy.append(float(line[1]))
                        Uz.append(float(line[2]))
                
                timestep.Ux, timestep.Uy, timestep.Uz = Ux, Uy, Uz

                data = {'U:0': timestep.Ux, 'U:1':timestep.Uy,'U:2':  timestep.Uz,'Points:0':self.points_x,'Points:1':self.points_y,'Points:2':self.points_z}
                df = pd.DataFrame(data, columns= ['U:0','U:1','U:2','Points:0','Points:1','Points:2'])
                df.to_csv(f"{self.ros_loc}/wind_simulations/{sim_arg}/wind_at_cell_centers_{step_idx}.csv",index=False,header=True)
            
            # gather .stls in ./environments/geometry and copy them to the gaden/envs/envname folder
            self.ros_cad_loc = f"{self.ros_loc}/cad_models/"
            stls = glob.glob(f"{self.settings['geometry_dir']}{env}/gaden/*.stl") # gather all stls
            stls_str = ' '.join([str(item) for item in stls])    # put them in one string separated by spaces
            os.system(f"cp {stls_str} {self.ros_cad_loc}")

            # get new empty point for source
            # self.place_source() # TODO move out

            # edit launch files
            self.ros_launch_folder = self.ros_loc + '/launch/'

            # GADEN_preprocessing.launch
            # TODO make specification for outlet CAD models flexible by inserting more lines (multiple outlets possible)
            with open(f"{self.ros_launch_folder}GADEN_preprocessing.launch", "r") as f:
                data = f.readlines()
            data[5] = f'    <arg name="scenario" default="{env}"/>\n'
            data[10] =f'        <param name="cell_size" value="{self.settings["cfd_mesh_settings"]["minCellSize"]}"/>\n' # set gas sim cell size to the cfd mesh size
            data[33] =f'        <param name="empty_point_x" value="{round(self.settings["src_placement"][0],2)}"/>      ### (m)\n'
            data[34] =f'        <param name="empty_point_y" value="{round(self.settings["src_placement"][1],2)}"/>      ### (m)\n'
            data[35] =f'        <param name="empty_point_z" value="{round(self.settings["src_placement"][2],2)}"/>      ### (m)\n'
            data[40] =f'        <param name="wind_files" value="$(find envs)/$(arg scenario)/wind_simulations/{sim_arg}/wind_at_cell_centers"/>\n'

            if self.settings["env_type"] == 'wh_empty': # delete interior cad model from launchfile
                data[13] = '        <param name="number_of_models" value="1"/>'
                data[15] = ''

            with open(f"{self.ros_launch_folder}GADEN_preprocessing.launch", "w") as f:
                f.writelines(data)
                f.close()

            # GADEN.launch # TODO add filament simulator settings and looping options
            with open(f"{self.ros_launch_folder}GADEN.launch", "r") as f:
                data = f.readlines()
            data[5] = f'    <arg name="scenario" default="{env}"/>\n'
            data[6] = f'    <arg name="simulation" default="{sim_arg}" />\n'
            data[7] = f'    <arg name="source_location_x" value="{"%.2f" % self.settings["src_placement"][0]}"/>      ### (m)\n'
            data[8] = f'    <arg name="source_location_y" value="{"%.2f" % self.settings["src_placement"][1]}"/>      ### (m)\n'
            data[9] = f'    <arg name="source_location_z" value="{"%.2f" % self.settings["src_placement"][2]}"/>      ### (m)\n'
            data[50] = f'	    <param name="sim_time" value="{self.settings["sim_time"]}" />                    ### [sec] Total time of the gas dispersion simulation\n'
            data[51] = f'	    <param name="time_step" value="{self.settings["time_step"]}" />                   ### [sec] Time increment between snapshots. Set aprox = cell_size/max_wind_speed.\n'
            data[58] = f'	    <param name="gas_type" value="{self.settings["gas_type"]}" />                      ### 0=Ethanol, 1=Methane, 2=Hydrogen, 6=Acetone\n'
            data[68] = f'	    <param name="wind_time_step" value="{self.settings["cfd_settings"]["writeInterval"]}" />                ### (sec) time increment between Wind snapshots\n'
            data[70] = f'        <param name="/allow_looping" value="{self.settings["wind_looping"]}" />\n'
            data[71] = f'        <param name="/loop_from_step" value="{self.settings["wind_start_step"]}" />\n'
            data[72] = f'        <param name="/loop_to_step" value="{self.settings["wind_stop_step"]}" />\n'

            with open(f"{self.ros_launch_folder}GADEN.launch", "w") as f:
                f.writelines(data)
                f.close()

            # GADEN_player.launch # TODO check for relevant CAD models and add/delete automatically
            with open(f"{self.ros_launch_folder}GADEN_player.launch", "r") as f:
                data = f.readlines()
            data[4] = f'    <arg name="scenario" default="{env}"/>\n'
            data[5] = f'    <arg name="simulation" default="{sim_arg}" />\n'
            data[6] = f'    <arg name="source_location_x" value="{"%.2f" % self.settings["src_placement"][0]}"/>      ### (m)\n'
            data[7] = f'    <arg name="source_location_y" value="{"%.2f" % self.settings["src_placement"][1]}"/>      ### (m)\n'
            data[8] = f'    <arg name="source_location_z" value="{"%.2f" % self.settings["src_placement"][2]}"/>      ### (m)\n'

            with open(f"{self.ros_launch_folder}GADEN_player.launch", "w") as f:
                f.writelines(data)
                f.close()
        
        self.remove_envs(invalid_idx) # remove the failed environments from the environment list

        self.printGDMStyle(f"[AutoGDM2] Prepared ROS.")


    # roslaunch GADEN preprocessing (adapted from AutoGDM)
    def run_preprocessing(self):
        self.printGDMStyle(f"[AutoGDM2] Preprocessing with GADEN...")
        for env in self.env_lst:
            self.printGDMStyle(f"[AutoGDM2] Preprocessing {env} with GADEN...")
            self.ros_loc = f"{self.settings['gaden_env_dir']}{env}"
            self.ros_launch_folder = self.ros_loc + '/launch/'
            os.system(f"cd {self.ros_launch_folder} && roslaunch GADEN_preprocessing.launch")
        
        self.printGDMStyle(f"[AutoGDM2] GADEN Preprocessing finished.")


    # roslaunch GADEN gas_simulator (adapted from AutoGDM)
    def run_ros(self):
        self.printGDMStyle(f"[AutoGDM2] Simulating gas dispersal with GADEN...")
        for env in self.env_lst:
            self.printGDMStyle(f"[AutoGDM2] Simulating gas dispersal for {env} with GADEN...")
            self.ros_loc = f"{self.settings['gaden_env_dir']}{env}"
            self.ros_launch_folder = self.ros_loc + '/launch/'
            os.system(f"cd {self.ros_launch_folder} && roslaunch GADEN.launch")

        self.printGDMStyle(f"[AutoGDM2] Finished gas dispersal simulation with GADEN...")

    # TODO - generate one array containing all gas iterations
    # compressed binary to numpy files for easy python use
    def gasdata_binary2npy(self, savetxt=False):
        for env_dir in self.env_lst:
            # create folder for the gas data output
            output_dir = f"{self.settings['gas_data_dir']}{env_dir}"
            if os.path.exists(output_dir): # if directory does already exist, delete
                os.system(f"rm -rf {output_dir}") # move to cleanup?
            os.mkdir(output_dir)

            gas_sim_dir = f"{self.settings['gaden_env_dir']}{env_dir}/gas_simulations/"
            current_dir = glob.glob(f"{gas_sim_dir}*/*/") # ! assuming there is only one sim case and one scenario

            files = os.listdir(current_dir[0])
            iterations = [str(item) for item in [x for x in files if 'wind' not in x]] # exclude 'wind' directory

            for iteration in iterations:
                filename = f"{current_dir[0]}{iteration}"
                header, filaments = read_gas_data(filename)
                output_file = f"{output_dir}/{iteration}"
                np.save(f"{output_file}_head.npy", header)
                np.save(f"{output_file}_fil.npy", filaments)
                
                if savetxt:
                    np.savetxt(f"{output_file}_head.txt", header, delimiter='\n')
                    np.savetxt(f"{output_file}_fil.txt", filaments)
        
        self.printGDMStyle(f"[AutoGDM2] Converdted gas dispersal data to numpy...")


    def windfields_binary2npy(self):
        for env_dir in self.env_lst:
            wind_sim_dir = f"{self.settings['gaden_env_dir']}{env_dir}/gas_simulations/"
            files = glob.glob(f"{wind_sim_dir}*/*/wind/*") # ! assuming there is only one sim case and one scenario

            windfields = read_wind_data(files)
            output_file = f"{self.settings['wind_data_dir']}/{env_dir}.npy"
            np.save(output_file, windfields)
            
        self.printGDMStyle(f"[AutoGDM2] Converted wind data data to numpy...")


    def occupancy_csv2npy(self):
        for env_dir in self.env_lst:
            file = f"{self.settings['gaden_env_dir']}{env_dir}/OccupancyGrid3D.csv"

            header, occ_grid = read_occ_csv(file)
            output_file = f"{self.settings['occ_data_dir']}/{env_dir}_grid.npy"
            np.save(output_file, occ_grid)

            with open(f"{self.settings['occ_data_dir']}/{env_dir}_head.txt", 'w') as convert_file:
                convert_file.write(json.dumps(header))
        
        self.printGDMStyle(f"[AutoGDM2] Converting occupancy data data to numpy...")


if __name__ == "__main__":
    start_time = datetime.now()
    conf = GDMConfig()
    settings = conf.current_gdm_settings()
    
    gdm = AutoGDM2(conf.current_gdm_settings())
    gdm.printGDMStyle(f"[AutoGDM2] --- CONFIG --- \n {conf.pretty(settings)}")
    
    gdm.cleanup()                 # clean AutoGDM directories and files
    gdm.layout_gen()              # create recipes for the desired environments
    gdm.blender_asset_placer()    # create .stl files of the mockup scenes used for cfd and GADEN
    gdm.isaac_asset_placer()      # create .usd scenes for use in Isaac Sim
    
    gdm.cfd_mesh()                # mesh the generated .stl files
    gdm.cfd_set_params()          # set the necessary cfd parameters
    gdm.cfd_run()                 # run the cfd simulation

    gdm.make_ros_folder()         # make ROS directories to run GADEN
    gdm.prep_ros()                # prepare ROS directory with environment-specific configurations
    gdm.run_preprocessing()       # roslaunch GADEN preprocessing
    gdm.run_ros()                 # roslaunch GADEN gas simulator

    gdm.gasdata_binary2npy()      # convert the generated gasdata to .npy and save in ./environemnts/gas_data/
    gdm.windfields_binary2npy()   # convert the generated windata to .npy and save in ./environments/wind_data/
    gdm.occupancy_csv2npy()       # convert the generated occupancy grid .csv to .npy and a header, save in ./environments/occupancy/
    
    gdm.printGDMStyle(f"[AutoGDM2] FINISEHD: Generated {settings['env_amount']} {settings['env_type']} environments in: \n {datetime.now() - start_time}")
    if gdm.env_lst_failed:
        gdm.printGDMStyle(f"[AUtoGDM2] Some environments failed and were not completed: \n {gdm.env_lst_failed}")