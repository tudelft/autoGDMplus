# AutoGDM+
### Automated Pipeline for 3D Gas Dispersal Modelling and Environment Generation

This repository contains the code of AutoGDM+ based on the same concepts as [AutoGDM](https://github.com/tudelft/AutoGDM/). Please fully read this before proceeding.

## Required
- Tested on `Ubuntu 20.04 LTS`
- [`Isaac Sim`](https://developer.nvidia.com/isaac-sim) (Install with the Omniverse Launcher)
- [`Blender`](https://www.blender.org/)
- [`OpenFOAM`]()
- [`ROS`](http://wiki.ros.org/noetic/Installation/Ubuntu) (noetic)

## Installation

### Omniverse Launcher & Isaac Sim
Follow [these instructions:](https://docs.omniverse.nvidia.com/install-guide/latest/standard-install.html)
1) Download, install and run the [`Omniverse Launcher`](https://www.nvidia.com/en-us/omniverse/). It is strongly recommended you install with the cache enabled. In case of problems see the troubleshooting section.
2) Create a local Nucleus server by going to the 'Nucleus' tab and enabling it. You will have to create an associated local Nucleus account (this is not associated with any other account). 

3) Install Isaac Sim version `2022.2.0`. Go to the 'exchange' tab and select Isaac Sim. Note, the default install location of Isaac Sim is `~/.local/share/ov/pkg/isaac_sim-<version>`
4) Download the necessery content:
    - From the the exchange tab in the launcher, download both the 'Industrial 3D Models Pack' and the 'USD Physics Sample Pack' by clicking 'Save as...' (right part of the green download button).
    - From the Nucleus tab in the launcher, go to `localhost/NVIDIA/Assets/Isaac/<version>/Isaac/Environments/Simple_Warehouse` and download these contents by clicking the download button in the details pane on the right.
    - Extract these folders to `~/Omniverse_content` so that AutoGDM+ can find them. Another location can be specified with in the settings of AutoGDM+ if placed somewhere else.

### Blender
- Download and extract the blender.zip to a location of your preference, in this case `~/Downloads/blender-<version>-linux-x64`

### Paraview (optional)
- For visualizing and verify the meshing and CFD results
```
sudo apt-get update && sudo apt-get install paraview
```

### OpenFOAM
1) Check the [system requirements](https://develop.openfoam.com/Development/openfoam/blob/develop/doc/Requirements.md)
2) Download the [OpenFoam](https://develop.openfoam.com/Development/openfoam) v2212 and its [Thirdparty software](https://develop.openfoam.com/Development/ThirdParty-common/) and extract in `~/OpenFOAM` such that the directories are called `OpenFOAM-<version>` and `Thirdparty-<version>`
3) Download and extract the source code of [scotch (v6.1.0)](https://gitlab.inria.fr/scotch/scotch/-/releases/v6.1.0) into the Thirdparty dicectory
4) Open a commandline in the home directory and check the system
```
source OpenFOAM/Openfoam-v2212/etc/bashrc && foamSystemCheck
```
5) `cd` into `~/OpenFOAM/OpenFOAM-v2212` and build:
```
./Allwmake -j -s -q -l
```
6) Add the following lines to your `.bashrc` to add an alias to source your OpenFOAM installation:
```
# >>> OpenFOAM >>>
alias of2212='source $HOME/OpenFOAM/OpenFOAM-v2212/etc/bashrc'
# <<< OpenFOAM <<<
```

### ROS & Catkin Tools
1) Install [ROS noetic](http://wiki.ros.org/noetic/Installation/Ubuntu)
2) Install [catkin tools](https://catkin-tools.readthedocs.io/en/latest/installing.html)

### AutoGDM+
- Clone this repository, preferably in your home directory.
- Install the isaac_asset_placer: Copy and paste the `warehouse_gen` folder into the Isaac Sim examples folder located at `~/.local/share/ov/pkg/isaac_sim-<version>/exts/omni.isaac.examples/omni/isaac/examples/`
- Build the GADEN workspace:
```
source /opt/ros/noetic/setup.bash
cd autoGDMplus/gaden_ws
catkin init
catkin build
```

## Before Running AutoGDM+
1) Check the asset file locations and software versions in `~/autoGDMplus/config/current.yaml`, especially:
    - `asset_dir` (line 8)
    - `isaac_wh_props` (line 80)
    - `forlift_asset` (line 93)
2) Define desired settings in `~/autoGDMplus/config/current.yaml`
3) Source your openfoam installation (with the previously created alias)
```
of2212
```
4) source the GADEN workspace
```
cd autoGDMplus/gaden_ws
source devel/setup.bash
```

## Run AutoGDM+
```
cd autoGDMplus
python3 main.py
```

## Troubleshooting
### Running AutoGDM+
- `could not find .../combined.fms` 
    - Solution: source your OpenFOAM installation before running
### Omniverse launcher
- [Stuck at login](https://forums.developer.nvidia.com/t/failed-to-login-stuck-after-logging-in-web-browser/260298/6) 
    - Solution: Search for the `nvidia-omniverse-launcher.desktop` file and copy it to `.config/autostart`


## Contact
Please reach out to us if you encounter any problems or suggestions. AutoGDM+ is a work in progress, we are excited to see it beeing used! Reach out to Hajo for all technical questions.

### Contributors
Hajo Erwich - Student & Maintainer - hajo_erwich@live.nl <br />
Bart Duisterhof - Supervisor & PhD Student <br />
Prof. Dr. Guido de Croon