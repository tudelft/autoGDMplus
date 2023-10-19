# Top level layout generator following the Isaac Sim Warehouse generator format
import json
import random
import numpy as np
from typing import Tuple

# TODO: remove member functions such as dx(), dy(), etc. and change them to attributes
class Asset:
    def __init__(self,
                 assetname:str      = "Asset",
                 fname:list         = [None, None], # [isaac_sim_asset, mockup_file]
                 dims:np.ndarray    = np.zeros(3),
                 loc:np.ndarray     = np.zeros(3),
                 ori:np.ndarray     = np.zeros(3),
                 scale:np.ndarray   = np.ones(3)
                 ) -> None:
        self.id = assetname
        self.fname = fname # [isaac_sim_asset, mockup_file]
        self.dims = dims
        self.ctr = 0.5*dims
        self.loc = loc
        self.ori = ori
        self.scale = scale

    def assetname(self) -> str:
        return self.id
    
    def set_assetname(self, assetname:str) -> None:
        self.id = assetname
        return

    def set_fname(self, fname:list) -> None:
        self.fname = fname
        return
   
    def dimensions(self) -> np.ndarray:
        return self.dims
    
    def set_dimensions(self, dims:np.ndarray=np.zeros(3)) -> None:
        self.dims = dims
        return

    def dx(self) -> float:
        return self.dims[0]
    
    def dy(self) -> float:
        return self.dims[1]
    
    def dz(self) -> float:
        return self.dims[2]
    
    def center(self) -> np.ndarray:
        return self.ctr
    
    def cx(self) -> float:
        return self.ctr[0]
    
    def cy(self) -> float:
        return self.ctr[1]
    
    def cz(self) -> float:
        return self.ctr[2]
    
    def location(self) -> np.ndarray:
        return self.loc
    
    def lx(self) -> float:
        return self.loc[0]
    
    def ly(self) -> float:
        return self.loc[1]
    
    def lz(self) -> float:
        return self.loc[2]
    
    def set_location(self, loc:np.ndarray) -> None:
        self.loc = loc
        return
    
    def translate(self, axis:str, amount:float) -> None:
        if axis == 'X':
            self.loc[0] = amount
        if axis == 'Y':
            self.loc[1] = amount
        if axis == 'Z':
            self.loc[2] = amount
    
    def set_orientation(self, ori:np.ndarray) -> None:
        self.ori = ori
        return
    
    def set_scale(self, scale:np.ndarray) -> None:
        self.scale = scale
        return
    
    def get_dict(self) -> dict:
        assetdict = {
            "asset_id": self.id,
            "filename": self.fname[0],
            "mockup_file": self.fname[1],
            "dimensions": self.dims.tolist(),
            "location": self.loc.tolist(),
            "orientation": self.ori.tolist(),
            "scale": self.scale.tolist()
        }
        return assetdict


class Warehouse:
    def __init__(self,
                 settings:dict,
                 wh_dims:np.ndarray     = np.array([10.0, 15.0, 9.0]),
                 inlet_dims:np.ndarray  = np.array([0.0,4.0,4.0]),
                 outlet_dims:np.ndarray = np.array([0.0,4.0,4.0])):
        self.settings = settings
        self.warehouse  = Asset("warehouse_shell", dims=wh_dims)
        self.floor      = Asset("floor", fname=self.settings['file_loc_paired']["floors"][0], dims=np.array([6.0, 6.0, 0.0]))
        self.cornerwall = Asset("cornerwall", dims=np.array([3.0,3.0,3.0]))
        self.wall       = Asset("wall", dims=np.array([0.0,6.0,3.0]))
        self.prop_light = Asset("prop_light", dims=np.array([2.0, 0.3, 3.0]))
        self.rect_light = Asset("rect_light", dims=np.array([self.warehouse.dx(), self.warehouse.dy(), 0.0]))
        self.rack       = Asset("rack", dims=np.array([1.0, 4.0, 3.0])) # default size of rack models
        self.rack_aisle = Asset("rack_aisle", dims=np.array([3.0, 0.0, 0.0]))
        self.end_aisle  = Asset("end_aisle", dims=np.array([0.0, (max(inlet_dims[1], outlet_dims[1]) + 2), 0.0]))
        self.forklift   = Asset("forklift", fname=self.settings['file_loc_paired']['forklift'][0], dims=np.array([0.8,1.0,2.0]))
        self.pile       = Asset("pile")
        self.inlet      = Asset("inlet", dims=inlet_dims)
        self.outlet     = Asset("outlet", dims=outlet_dims)


    # returns arrays of rack positions (centered for each rack)
    def rack_positions(self) -> np.ndarray:
        rack_orig = np.array([self.rack.cx(), self.rack.cy() + self.end_aisle.dy(), 0.0]) # origin of rack array
        rack_rows = int(1 + (self.warehouse.dx()-self.rack.dx()) // (self.rack.dx() + self.rack_aisle.dx()))
        rack_segs = int((self.warehouse.dy() - (2 * self.end_aisle.dy())) // self.rack.dy())
        rack_stack= int((self.warehouse.dz()) // self.rack.dz()) # height

        nx, ny, nz = rack_rows, rack_segs, rack_stack
        x = np.linspace(rack_orig[0], self.warehouse.dx() - 0.5 * self.rack.dx(), nx)
        y = np.linspace(rack_orig[1], rack_orig[1] + (self.rack.dy() * (ny-1)), ny)
        z = np.arange(rack_orig[2], self.rack.dz() * nz, self.rack.dz())
        xv, yv, zv = np.meshgrid(x,y,z) # generate grid and reshape array for ease of use
        stack = np.stack([xv, yv, zv], -1)
        positions = stack.reshape(np.prod(stack.shape[0:-1]),3)

        return positions


    # divides positions, affects empty/filled rack ratio
    def position_division(self, divisor:float ,positions:np.ndarray=np.zeros(3)) -> np.ndarray:
        totalSample = positions.shape[0]
        minSample = int((totalSample//(divisor**-1)))
        sampleSize = np.random.randint(minSample,totalSample)
        idx = random.sample(range(totalSample),sampleSize)
        filledRackPos, emptyRackPos = positions[idx,:], np.delete(positions, idx, 0)
        return filledRackPos, emptyRackPos


    # TODO - hardcoded for now, make scalable
    def complex_positions(self) -> np.ndarray:
        edge_dist = 2.0
        x = np.linspace(edge_dist, (15-edge_dist), 4)
        y = np.linspace(1.5, (15-1.5), 4)
        
        positions = np.array([[x[0], y[0], 0.0],
                              [x[0], y[1], 0.0],
                              [x[0], y[2], 0.0],
                              [x[0], y[3], 0.0],
                              [x[1], y[3], 0.0],
                              [x[2], y[3], 0.0],
                              [x[3], y[3], 0.0],
                              [x[3], y[2], 0.0],
                              [x[3], y[1], 0.0],
                              [x[3], y[0], 0.0],
                              [x[2], y[0], 0.0],
                              [x[1], y[0], 0.0]])
        
        return positions


    # interior dict generation
    def interior_gen(self, filled:np.ndarray, empty:np.ndarray, comp_loc:np.ndarray=None) -> list:
        interior_dicts = []
        scale_factor = np.array([0.01, 0.01, 0.01]) # custom scaling factor

        # filled racks
        for i,loc in enumerate(filled):
            self.rack.set_assetname(f"filled_rack_{str(i).zfill(3)}")
            self.rack.set_fname(random.choice(self.settings['file_loc_paired']["filled_racks"])) # choose random type of rack and corresponding mockup
            self.rack.set_orientation(np.zeros(3,))
            self.rack.set_location(loc)
            self.rack.set_scale(scale_factor)

            if comp_loc is not None and loc[0] > 1.0 and loc[0] < 14.0: # TODO : remove hardcoded orientation
                self.rack.set_orientation(np.array([0,0,90]))

            interior_dicts.append(self.rack.get_dict())

        # empty racks
        for i,loc in enumerate(empty):
            self.rack.set_assetname(f"empty_rack_{str(i).zfill(3)}")
            self.rack.set_fname(random.choice(self.settings['file_loc_paired']["empty_racks"])) # choose random type of rack and corresponding mockup
            self.rack.set_orientation(np.zeros(3,))
            self.rack.set_location(loc)
            self.rack.set_scale(scale_factor)

            if comp_loc is not None and loc[0] > 1.0 and loc[0] < 14.0: # TODO : remove hardcoded orientation
                self.rack.set_orientation(np.array([0,0,90]))

            interior_dicts.append(self.rack.get_dict())

        if comp_loc is not None:
            # get 4 random indices
            idx = np.random.choice(11, 6, replace=False)
            forklift_idx = idx[0]
            piles_idx = idx[1:]
            
            # add forklift to dict
            self.forklift.set_location(comp_loc[forklift_idx])
            self.forklift.set_orientation(np.array([0.0,0.0,np.random.randint(0,359)]))
            self.forklift.set_scale(scale_factor)
            interior_dicts.append(self.forklift.get_dict())

            # add piles to dict
            for i,loc in enumerate(comp_loc[piles_idx]):
                self.pile.set_assetname(f"pile_{str(i).zfill(3)}")
                self.pile.set_fname(random.choice(self.settings['file_loc_paired']["piles"])) # choose random type of pile and corresponding mockup
                self.pile.set_location(loc)
                self.pile.set_orientation(np.array([0.0,0.0,np.random.randint(0,359)]))
                self.pile.set_scale(scale_factor)
                interior_dicts.append(self.pile.get_dict())

        return interior_dicts


    ################
    ### CFD MESH ###
    ################
    # The CFD mesh is generated using assets that blender can place and save to .stl

    # sides dict generation, these are all planes
    def sides_blender(self) -> list:
        side_dicts = []
        # bottom
        bottom = Asset("bottom",dims=np.array([self.warehouse.dx(), self.warehouse.dy(), 0.0]),
                      loc=0.5*np.array([self.warehouse.dx(), self.warehouse.dy(), 0]))
        side_dicts.append(bottom.get_dict())
        # top
        top = Asset("top",dims=np.array([self.warehouse.dx(), self.warehouse.dy(), 0.0]),
                      loc=np.array([0.5*self.warehouse.dx(),0.5*self.warehouse.dy(), self.warehouse.dz()]),
                      ori=np.array([180,0,0])) # important for the face normals to point inside
        side_dicts.append(top.get_dict())
        # front
        front = Asset("front",dims=np.array([self.warehouse.dx(), self.warehouse.dz(), 0.0]),
                      loc=np.array([0.5*self.warehouse.dx(),0,0.5*self.warehouse.dz()]),
                      ori=np.array([-90,0,0]))
        side_dicts.append(front.get_dict())
        # back
        back = Asset("back",dims=np.array([self.warehouse.dx(), self.warehouse.dz(), 0.0]),
                loc=np.array([0.5*self.warehouse.dx(),self.warehouse.dy(),0.5*self.warehouse.dz()]),
                ori=np.array([90,0,0]))
        side_dicts.append(back.get_dict())
        # inlet side
        side1 = Asset("side_001",dims=np.array([self.warehouse.dz(), self.warehouse.dy()-self.inlet.dy(), 0.0]),
                loc=np.array([0.0, 0.5*(self.warehouse.dy()+self.inlet.dy()), 0.5*self.warehouse.dz()]),
                ori=np.array([0,90,0]))
        side_dicts.append(side1.get_dict())

        side2 = Asset("side_002",dims=np.array([self.warehouse.dz()-self.inlet.dz(), self.inlet.dy(), 0.0]),
                loc=np.array([0.0, 0.5*self.inlet.dy(), 0.5*(self.warehouse.dz()+self.inlet.dz())]),
                ori=np.array([0,90,0]))
        side_dicts.append(side2.get_dict())
        # oulet side
        side3 = Asset("side_003",dims=np.array([self.warehouse.dz(), self.warehouse.dy()-self.outlet.dy(), 0.0]),
                loc=np.array([self.warehouse.dx(), 0.5*(self.warehouse.dy()-self.outlet.dy()), 0.5*self.warehouse.dz()]),
                ori=np.array([0,-90,0]))
        side_dicts.append(side3.get_dict())

        side4 = Asset("side_004",dims=np.array([self.warehouse.dz()-self.outlet.dz(), self.outlet.dy(), 0.0]),
                loc=np.array([self.warehouse.dx(), self.warehouse.dy()-0.5*self.outlet.dy(), 0.5*(self.warehouse.dz()+self.outlet.dz())]),
                ori=np.array([0,-90,0]))
        side_dicts.append(side4.get_dict())

        return side_dicts
    
    def inlets_blender(self) -> list:
        inlet_dicts = []
        inlet = Asset("inlet001",dims=np.array([self.inlet.dz(), self.inlet.dy(), 0.0]),
                loc=np.array([0.0, 0.5*self.inlet.dy(), 0.5*self.inlet.dz()]),
                ori=np.array([0,90,0]))
        inlet_dicts.append(inlet.get_dict())
        return inlet_dicts

    def outlets_blender(self) -> list:
        outlet_dicts = []
        outlet = Asset("outlet001",dims=np.array([self.outlet.dz(), self.outlet.dy(), 0.0]),
                 loc=np.array([self.warehouse.dx(), self.warehouse.dy()-0.5*self.outlet.dy(), 0.5*self.outlet.dz()]),
                 ori=np.array([0,-90,0]))
        outlet_dicts.append(outlet.get_dict())
        return outlet_dicts

    ################
    ###  GADEN   ###
    ################
    # gaden requires additional geometry with thickness such as the walls, inlet and outlets
    # for this, blender will need to perform boolean operations
    # first all geometry is given. lastly, a separate dict entry is used for the boolean operations

    def gaden_geom(self) -> Tuple[list,list]:
        gaden_geom_dicts = []
        gaden_bools = []

        wallthickness = 0.2
        walls = Asset("walls", dims=np.array([self.warehouse.dx()+2*wallthickness, self.warehouse.dy()+2*wallthickness, self.warehouse.dz()]),
                      loc=self.warehouse.center())
        gaden_geom_dicts.append(walls.get_dict())

        inside = Asset("inside", dims=np.array([self.warehouse.dx(),self.warehouse.dy(),self.warehouse.dz()+1.0]),
                      loc=self.warehouse.center())
        gaden_geom_dicts.append(inside.get_dict())

        inlet = Asset("inlet", dims=np.array([wallthickness+0.2, self.inlet.dy(), self.inlet.dz()]),
                      loc=np.array([-0.5*wallthickness, 0.5*self.inlet.dy(), 0.5*self.inlet.dz()]))
        gaden_geom_dicts.append(inlet.get_dict())

        outlet = Asset("outlet", dims=np.array([wallthickness+0.2, self.outlet.dy(), self.outlet.dz()]),
                      loc=np.array([self.warehouse.dx()+ 0.5*wallthickness, self.warehouse.dy()-0.5*self.outlet.dy(), 0.5*self.outlet.dz()]))
        gaden_geom_dicts.append(outlet.get_dict())

        for asset in [inside, inlet, outlet]:
            gaden_bools.append([walls.get_dict(), asset.get_dict(), 'DIFFERENCE'])

        return gaden_geom_dicts, gaden_bools


    ################
    ###  ISAAC   ###
    ################
    def isaac_floor_dicts(self) -> list:
        floor_orig = np.array([self.floor.cx(), self.floor.cy(), 0.0]) # origin of floor array
        floor_rows = int(np.ceil(self.warehouse.dx()/self.floor.dx())) # floor tile rows (round up)
        floor_cols = int(np.ceil(self.warehouse.dy()/self.floor.dy())) # floor tile columns (round up)

        nx, ny = floor_rows, floor_cols
        x = np.linspace(floor_orig[0], floor_orig[0] + self.floor.dx()*(nx-1), nx)
        y = np.linspace(floor_orig[1], floor_orig[1] + self.floor.dy()*(ny-1), ny)

        xv, yv = np.meshgrid(x,y) # generate grid and reshape array for ease of use
        zv = np.zeros_like(xv)
        stack = np.stack([xv, yv, zv], -1)
        positions = stack.reshape(np.prod(stack.shape[0:-1]),3)
        
        floor_tile_dicts = []
        for i,loc in enumerate(positions):
            self.floor.set_assetname(f"floor_tile_{str(i).zfill(3)}")
            self.floor.set_location(loc)
            floor_tile_dicts.append(self.floor.get_dict())
        
        return floor_tile_dicts
    

    def isaac_walls_dicts(self) -> list:
        walls_dicts = []
        
        # walls are made higher than env size to accomodate the lighting
        ceiling_height = self.warehouse.dz() + self.prop_light.dz()

        # corners
        nz = int(np.ceil(ceiling_height/self.cornerwall.dz()))
        z = np.linspace(0.0, self.wall.dz() * (nz-1), nz)
        z[-1] = ceiling_height - self.cornerwall.dz()

        if self.settings["white_walls"]:
            walltypes = np.zeros(nz, dtype=int) # white walls only
        else:
            walltypes = np.ones(nz, dtype=int) # default white and yellow walls
            walltypes[0] = 0
        
        x = np.linspace(0.0, self.warehouse.dx(), 2)
        y = np.linspace(0.0, self.warehouse.dy(), 2)
        ori = np.array([[90., 180., 0., 270.]])

        xv, yv = np.meshgrid(x,y)
        stack = np.stack([xv, yv], -1)
        positions = stack.reshape((4,2))
        transforms = np.hstack((positions, ori.T)) # [X Y Z-rotation]      
        
        for i, (z_pos, walltype) in enumerate(zip(z, walltypes)):
            for j,transform in enumerate(transforms):
                self.cornerwall.set_assetname(f"wall_corner_{i}_{j}")
                self.cornerwall.set_fname(self.settings['file_loc_paired']["walls"][walltype])
                self.cornerwall.set_location(np.array([transform[0], transform[1], z_pos]))
                self.cornerwall.set_orientation(np.array([0.0,0.0,transform[2]]))
                walls_dicts.append(self.cornerwall.get_dict())

        # flat walls
        nz = int(np.ceil(ceiling_height/self.wall.dz()))
        z = np.linspace(0.0, self.wall.dz() * (nz-1), nz)
        z[-1] = ceiling_height - self.wall.dz()

        if self.settings["white_walls"]:
            walltypes = np.zeros(nz, dtype=int) # white walls only
        else:
            walltypes = np.ones(nz, dtype=int) # default white and yellow walls
            walltypes[0] = 0      
        
        # check if additional walls are needed for x direction
        if self.warehouse.dx() > (2 * self.cornerwall.dx()):            
            # walls in x-dir
            nx = int(np.ceil((self.warehouse.dx()-(2*self.cornerwall.dx()))/self.wall.dy()))
            x = np.linspace(self.cornerwall.dx() + self.wall.cy(), self.warehouse.dx() - (self.cornerwall.dx() + self.wall.cy()), nx)

            y = np.linspace(0.0, self.warehouse.dy(), 2)
            ori = np.linspace(90.0, -90.0, 2)

            for i, (z_pos, walltype) in enumerate(zip(z, walltypes)):
                for j, (y_pos, orientation) in enumerate(zip(y, ori)):
                    for k, x_pos in enumerate(x):
                        self.wall.set_assetname(f"wallX_{i}_{k}_{j}")
                        self.wall.set_fname(self.settings['file_loc_paired']["walls"][2+walltype])
                        self.wall.set_location(np.array([x_pos, y_pos, z_pos]))
                        self.wall.set_orientation(np.array([0.0, 0.0, orientation]))
                        walls_dicts.append(self.wall.get_dict())

        # check if additional walls are needed for y direction
        if self.warehouse.dy() > (2 * self.cornerwall.dy()):  
            # walls in y-dir
            ny = int(np.ceil((self.warehouse.dy()-(2*self.cornerwall.dy()))/self.wall.dy()))
            y = np.linspace(self.cornerwall.dy() + self.wall.cy(), self.warehouse.dy() - (self.cornerwall.dy() + self.wall.cy()), ny)

            x = np.linspace(0.0, self.warehouse.dx(), 2)
            ori = np.linspace(0.0, 180, 2)

            for i, (z_pos, walltype) in enumerate(zip(z, walltypes)):
                for j, (x_pos, orientation) in enumerate(zip(x, ori)):
                    for k, y_pos in enumerate(y):
                        self.wall.set_assetname(f"wallY_{i}_{k}_{j}")
                        self.wall.set_fname(self.settings['file_loc_paired']["walls"][2+walltype])
                        self.wall.set_location(np.array([x_pos, y_pos, z_pos]))
                        self.wall.set_orientation(np.array([0.0, 0.0, orientation]))
                        walls_dicts.append(self.wall.get_dict())
    
        return walls_dicts


    def isaac_lights_dicts(self) -> list:
        prop_lights_dicts = []
        # rect_lights_dicts = []

        z_rect_light = self.warehouse.dz()
        z_lights = z_rect_light + self.prop_light.dz()
        spacing_xy = [2.5, 4.0]

        # decorative (prop) lights
        nx = int(np.ceil(((self.warehouse.dx()-(2*spacing_xy[0]))/spacing_xy[0])))
        ny = int(np.ceil(((self.warehouse.dy()-(2*spacing_xy[1]))/spacing_xy[1])))

        x = np.linspace(spacing_xy[0], self.warehouse.dx()-spacing_xy[0], nx)
        y = np.linspace(spacing_xy[1], self.warehouse.dy()-spacing_xy[1], ny)

        xv, yv = np.meshgrid(x,y) # generate grid and reshape array for ease of use
        zv = z_lights * np.ones_like(xv)
        stack = np.stack([xv, yv, zv], -1)
        positions = stack.reshape(np.prod(stack.shape[0:-1]),3)
        
        for i, pos in enumerate(positions):
            self.prop_light.set_assetname(f"light_{str(i).zfill(3)}")
            self.prop_light.set_fname(self.settings['file_loc_paired']["lights"][1])
            self.prop_light.set_location(np.array([pos[0], pos[1], pos[2]]))
            self.prop_light.set_orientation(np.array([0.0,0.0,90.0]))
            prop_lights_dicts.append(self.prop_light.get_dict())

        # rectangular light over the whole scene TODO: Add temperature and intensity?
        # self.rect_light.set_location(np.array([self.warehouse.cx(), self.warehouse.cy(), z_rect_light]))
        # self.rect_light.set_scale(self.rect_light.dimensions())
        # rect_lights_dicts.append(self.rect_light.get_dict())

        return prop_lights_dicts #, rect_lights_dicts


def generate_recipes(settings:dict) -> None:
    recipe_dict = {}
    
    if 'wh' in settings["env_type"]:
        recipe_dict["env_type"]   = settings["env_type"]
        recipe_dict["env_size"]   = settings["env_size"]
        recipe_dict["inlet_size"] = settings["inlet_size"]
        recipe_dict["oulet_size"] = settings["outlet_size"]
        
        for i in range(settings["env_amount"]):
            env_id = str(i).zfill(4)
            recipe_dict["env_id"] =  env_id
            wh = Warehouse(settings,
                           wh_dims=np.array([recipe_dict["env_size"][0], recipe_dict["env_size"][1], recipe_dict["env_size"][2]]),
                           inlet_dims=np.array([0.0,recipe_dict["inlet_size"][0],recipe_dict["inlet_size"][1]]),
                           outlet_dims=np.array([0.0,recipe_dict["inlet_size"][0],recipe_dict["inlet_size"][1]]))
            
            # CFD mesh geometry 
            recipe_dict["sides"]    = wh.sides_blender()
            recipe_dict["inlets"]   = wh.inlets_blender()
            recipe_dict["outlets"]  = wh.outlets_blender()

            # CFD mesh and Isaac Sim interior geometry
            if 'empty' in settings["env_type"]:
                recipe_dict["interior"] = {}
            else:
                positions = wh.rack_positions()
                filled_locs, empty_locs = wh.position_division(settings["emptyfullrackdiv"],positions)
                
                if 'complex' in settings["env_type"]: 
                    complex_pos = wh.complex_positions()
                else:
                    complex_pos = None

                recipe_dict["interior"] = wh.interior_gen(filled_locs, empty_locs, comp_loc=complex_pos)

            # GADEN geometry
            recipe_dict["gaden_geom"], recipe_dict["gaden_bools"] = wh.gaden_geom()

            # Isaac Sim geometry
            recipe_dict["isaac_floor"] = wh.isaac_floor_dicts()
            recipe_dict["isaac_walls"] = wh.isaac_walls_dicts()
            recipe_dict["isaac_lights"] = wh.isaac_lights_dicts()

            # write dictionary
            with open(f'{settings["recipe_dir"]}{settings["env_type"]}_{env_id}.txt', 'w') as convert_file:
                convert_file.write(json.dumps(recipe_dict))
    
    # TODO: create more environments
