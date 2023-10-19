import random, math
NUCLEUS_SERVER_CUSTOM = "/home/hajo/Omniverse_content/ov-industrial3dpack-01-100.1.1/"
SIMPLE_WAREHOUSE = "~/Omniverse_content/isaac-simple-warehouse/"

# This file contains dictionaries for different genration recipes - you can create your own here and expand the database!
# You can also edit existing to see how your rules generate scenes!

# Rule based placers (XYZ Locations based on Procedural or User-selected layout)
# X = columns; distance between racks (675 is width of rack) // Y = height // Z = rows

# R A C  K S
divisor = 2
def racks_procedural():
    positions = []
    for i in range(9):
        positions.extend(
            [
                (2800 - (i * 675), 0, 1888),
                (2800 - (i * 675), 0, 962),
                (2800 - (i * 675), 0, 513),
                (2800 - (i * 675), 0, -1034),
                (2800 - (i * 675), 0, -1820),
            ]
        )
    totalSample = len(positions)
    minSample = math.floor(totalSample/divisor)
    sampleSize = random.randint(minSample,totalSample)
    filledRackPos = [positions.pop(random.randrange(len(positions))) for _ in range(sampleSize)]
    emptyRackPos = positions
    return filledRackPos, emptyRackPos

def empty_racks_Umode():
    positions = []
    for i in range(9):
        if i < 5:
            positions.extend([(2800 - (i * 675), 0, 1888),  (2800 - (i * 675), 0, -1820), (2800 - (i * 675), 0, -2225)])
        else:
            positions.extend(
                [
                    (2800 - (i * 675), 0, 1888),
                    (2800 - (i * 675), 0, 962),
                    (2800 - (i * 675), 0, 513),
                    (2800 - (i * 675), 0, -1034),
                    (2800 - (i * 675), 0, -1820),
                ]
            )
    totalSample = len(positions)
    minSample = math.floor(totalSample/divisor)
    sampleSize = random.randint(minSample,totalSample)
    filledRackPos = [positions.pop(random.randrange(len(positions))) for _ in range(sampleSize)]
    emptyRackPos = positions
    return filledRackPos, emptyRackPos


def empty_racks_Lmode():
    positions = []
    for i in range(9):
        if i < 5:
            positions.extend([(2800 - (i * 675), 0, 1888), (2800 - (i * 675), 0, 962), (2800 - (i * 675), 0, 513)])
        else:
            positions.extend(
                [
                    (2800 - (i * 675), 0, 1888),
                    (2800 - (i * 675), 0, 962),
                    (2800 - (i * 675), 0, 513),
                    (2800 - (i * 675), 0, -1034),
                    (2800 - (i * 675), 0, -1820),
                ]
            )
    totalSample = len(positions)
    minSample = math.floor(totalSample/divisor)
    sampleSize = random.randint(minSample,totalSample)
    filledRackPos = [positions.pop(random.randrange(len(positions))) for _ in range(sampleSize)]
    emptyRackPos = positions
    return filledRackPos, emptyRackPos

def empty_racks_Imode():
    positions = []
    for i in range(9):
        positions.extend(
            [
                (2800 - (i * 675), 0, 962),
                (2800 - (i * 675), 0, 513),
                (2800 - (i * 675), 0, -1034)
            ]
        )
    totalSample = len(positions)
    minSample = math.floor(totalSample/divisor)
    sampleSize = random.randint(minSample,totalSample)
    filledRackPos = [positions.pop(random.randrange(len(positions))) for _ in range(sampleSize)]
    emptyRackPos = positions
    return filledRackPos, emptyRackPos

## P I L E S

def piles_placer_procedural():
    positions = []
    for i in range(9):
        positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, 35), (2947 - (i * 675), 0, -1440)])
    # print("pile positions (procedural): ", positions)
    return positions

def piles_placer_Umode():
    positions = []
    for i in range(9):
        if i < 5:
            positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, -1440)])
        else:
            positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, 35), (2947 - (i * 675), 0, -1440)])
    return positions

def piles_placer_Imode():
    positions = []
    for i in range(9):
        positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, 35), (2947 - (i * 675), 0, -1440)])
    return positions

def piles_placer_Lmode():
    positions = []
    for i in range(9):
        if i<5:
            positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, 35)])
        else:
            positions.extend([(2744.5 - (i * 675), 0, 1384), (2947 - (i * 675), 0, 35), (2947 - (i * 675), 0, -1440)])
    return positions

## R A I L I N G S
def railings_placer_procedural():
    positions = []
    for i in range(17):
        positions.extend([(3017 - (i * 337.5), 0, -119)])
    return positions

def railings_placer_Lmode():
    positions = []
    for i in range(17):
        positions.extend([(3017 - (i * 337.5), 0, -119)])
    return positions

def railings_placer_Umode():
    positions = []
    for i in range(9,17):
        positions.extend([(3017 - (i * 337.5), 0, -119)])
    return positions

def railings_placer_Imode():
    positions = []
    for i in range(17):
        positions.extend([(3017 - (i * 337.5), 0, -119)])
    return positions



# R O B O T / F O R K L I F T

def robo_fork_placer_procedural(posXYZ):
    positions = []
    for i in range(17):
        positions.extend([(posXYZ[0] - (i * 337.5), posXYZ[1], posXYZ[2])])
    return positions

def robo_fork_placer_Lmode(posXYZ):
    positions = []
    for i in range(10,17):
        positions.extend([(posXYZ[0] - (i * 337.5), posXYZ[1], posXYZ[2])])
    return positions

def robo_fork_placer_Umode(posXYZ):
    positions = []
    for i in range(9,17):
        positions.extend([(posXYZ[0] - (i * 337.5), posXYZ[1], posXYZ[2])])
    return positions

def robo_fork_placer_Imode(posXYZ):
    positions = []
    for i in range(17):
        positions.extend([(posXYZ[0] - (i * 337.5), posXYZ[1], posXYZ[2])])
    return positions

# Store rack position data
filledProcMode, emptyProcMode = racks_procedural()
filledUMode, emptyUMode = empty_racks_Umode()
filledLMode, emptyLMode = empty_racks_Lmode()
filledIMode, emptyIMode = empty_racks_Imode()

warehouse_recipe_custom = {
    # First step is to identify what mode the generation is, we have 4 modes. By default, we will keep it at procedural.
    # If it is a customized generation, we can update this value to the layout type chosen from the UI
    # P.S : "procedural" mode is basically I-Shaped (Imode) with all objects selected
    "mode": "procedural",
    # Then, we point to asset paths, to pick one at random and spawn at specific positions
    "empty_racks": f"{NUCLEUS_SERVER_CUSTOM}Shelves/",
    "filled_racks": f"{NUCLEUS_SERVER_CUSTOM}Racks/",
    "piles": f"{NUCLEUS_SERVER_CUSTOM}Piles/",
    "railings": f"{NUCLEUS_SERVER_CUSTOM}Railing/",
    "forklift": f"/home/hajo/Omniverse_content/ov-sig22-physics-01-100.1.0/Assets/Warehouse/Equipment/Forklifts/Forklift_A/",
    "robot": f"http://omniverse-content-staging.s3-us-west-2.amazonaws.com/Assets/Isaac/2022.1/Isaac/Robots/Transporter/",
    # we can also have stand-alone assets, that are directly spawned in specific positions
    "forklift_asset": ["Forklift_A01_PR_V_NVD_01.usd"],
    "robot_asset": ["transporter.usd"],
    # We are also adding other assets from the paths above to choose from
    "empty_racks_asset": ["RackLargeEmpty_A1.usd", "RackLargeEmpty_A2.usd"],
    "filled_racks_asset": [
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
    # Now, we have a sample space of positions within the default warehouse shell these objects can go to. We can randomly
    # spawn prims into randomly selected positions from this sample space. These are either generated by placer functions,
    # or hardcoded for standalone assets
    # Empty and Filled racks both have similar dimensions, so we reuse the positions for racks
    "filled_racks_procedural": filledProcMode,
    "empty_racks_procedural": emptyProcMode,
    "filled_racks_Umode": filledUMode,
    "empty_racks_Umode": emptyUMode,
    "filled_racks_Lmode": filledLMode,
    "empty_racks_Lmode": emptyLMode,
    "filled_racks_Imode": filledIMode,
    "empty_racks_Imode": emptyIMode,
    # Piles (Rules doesnt change based on layout mode here. Feel free to update rules)
    "piles_procedural": piles_placer_procedural(),
    "piles_Umode": piles_placer_Umode(),
    "piles_Lmode": piles_placer_Lmode(),
    "piles_Imode": piles_placer_Imode(),
    # Railings (Similar to piles)
    "railings_procedural": railings_placer_procedural(),
    "railings_Umode": railings_placer_Umode(),
    "railings_Lmode": railings_placer_Lmode(),
    "railings_Imode": railings_placer_Imode(),

    # Forklift and Robot
    "forklift_procedural": robo_fork_placer_procedural((2500, 0, -333)),
    "forklift_Umode": robo_fork_placer_Umode((2500, 0, -333)),
    "forklift_Lmode": robo_fork_placer_Lmode((2500, 0, -333)),
    "forklift_Imode": robo_fork_placer_Imode((2500, 0, -333)),

    "robot_procedural": robo_fork_placer_procedural((3017, 8.2, -698)),
    "robot_Umode": robo_fork_placer_Umode((3017, 8.2, -698)),
    "robot_Lmode": robo_fork_placer_Lmode((3017, 8.2, -698)),
    "robot_Imode": robo_fork_placer_Imode((3017, 8.2, -698)),    
}

warehouse_recipe_simple = {
    # First step is to identify what mode the generation is, we have 4 modes. By default, we will keep it at procedural.
    # If it is a customized generation, we can update this value to the layout type chosen from the UI
    # P.S : "procedural" mode is basically I-Shaped (Imode) with all objects selected
    "mode": "procedural",
    # Then, we point to asset paths, to pick one at random and spawn at specific positions
    "empty_racks": f"{NUCLEUS_SERVER_CUSTOM}Shelves/",
    "filled_racks": f"{NUCLEUS_SERVER_CUSTOM}Racks/",
    "piles": f"{NUCLEUS_SERVER_CUSTOM}Piles/",
    "railings": f"{NUCLEUS_SERVER_CUSTOM}Railing/",
    "forklift": f"/home/hajo/Omniverse_content/ov-sig22-physics-01-100.1.0/Assets/Warehouse/Equipment/Forklifts/Forklift_A/",
    "robot": f"http://omniverse-content-staging.s3-us-west-2.amazonaws.com/Assets/Isaac/2022.1/Isaac/Robots/Transporter/",
    # we can also have stand-alone assets, that are directly spawned in specific positions
    "forklift_asset": ["Forklift_A01_PR_V_NVD_01.usd"],
    "robot_asset": ["transporter.usd"],
    # We are also adding other assets from the paths above to choose from
    "empty_racks_asset": ["RackLargeEmpty_A1.usd", "RackLargeEmpty_A2.usd"],
    "filled_racks_asset": [
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
    # Now, we have a sample space of positions within the default warehouse shell these objects can go to. We can randomly
    # spawn prims into randomly selected positions from this sample space. These are either generated by placer functions,
    # or hardcoded for standalone assets
    # Empty and Filled racks both have similar dimensions, so we reuse the positions for racks
    "filled_racks_procedural": filledProcMode,
    "empty_racks_procedural": emptyProcMode,
    "filled_racks_Umode": filledUMode,
    "empty_racks_Umode": emptyUMode,
    "filled_racks_Lmode": filledLMode,
    "empty_racks_Lmode": emptyLMode,
    "filled_racks_Imode": filledIMode,
    "empty_racks_Imode": emptyIMode,
    # Piles (Rules doesnt change based on layout mode here. Feel free to update rules)
    "piles_procedural": piles_placer_procedural(),
    "piles_Umode": piles_placer_Umode(),
    "piles_Lmode": piles_placer_Lmode(),
    "piles_Imode": piles_placer_Imode(),
    # Railings (Similar to piles)
    "railings_procedural": railings_placer_procedural(),
    "railings_Umode": railings_placer_Umode(),
    "railings_Lmode": railings_placer_Lmode(),
    "railings_Imode": railings_placer_Imode(),

    # Forklift and Robot
    "forklift_procedural": robo_fork_placer_procedural((2500, 0, -333)),
    "forklift_Umode": robo_fork_placer_Umode((2500, 0, -333)),
    "forklift_Lmode": robo_fork_placer_Lmode((2500, 0, -333)),
    "forklift_Imode": robo_fork_placer_Imode((2500, 0, -333)),

    "robot_procedural": robo_fork_placer_procedural((3017, 8.2, -698)),
    "robot_Umode": robo_fork_placer_Umode((3017, 8.2, -698)),
    "robot_Lmode": robo_fork_placer_Lmode((3017, 8.2, -698)),
    "robot_Imode": robo_fork_placer_Imode((3017, 8.2, -698)),    
}