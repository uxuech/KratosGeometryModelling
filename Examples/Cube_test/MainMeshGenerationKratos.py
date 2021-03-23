

# importing external classes in order to build tridimensional terrain mesh automatycally 
from contour_input_output import ContourInputOutput
# from gmsh_contout_2d_mesh import GmshContour2dMeshGenerator
# from simulation_mesh_medpa import SimulationMeshMdpa
# from gmsh_3d_mesh_terrain import Gmsh3dMeshTerrain
# from kratos_terrain_elevation import TerrainElevationFromRaster
import KratosMultiphysics
# VARIABLES THAT SHOULD BE CHOOSED BY USERS
# 1. Shapefile name and file and path in order to get it 
# 2. mdpa name 2d ( necesario )
# 3. ModelPartName???
# 4. Raster name
# 5. Mesh size
# 6. output mdpa 3d name
# 7. optional features: Rounded....etc 
# 8. movement to origin
#
#
#and extracted from other classes 
#TODO: We need to read geoprojectparameters.json
# we are normalizing data base extracted from a shapefile in order to use gmsh meshing tools

default_settings = KratosMultiphysics.Parameters("""
        {
        	"file_name":"CubeTest",
        	"round_coordinates": true,
        	"file_format":".shp",
        	"move_to_origen":true,
        	"tolerance_repeated_points":1e-5
            
        }""")





ContourInputOutput(default_settings).Execute()
#1. Initially 2d contour mesh will be defined and mdpa to Kratos is built
# GmshContour2dMeshGenerator(default_settings).Execute()
# TerrainElevationFromRaster(default_settings).Execute()
# Gmsh3dMeshTerrain(default_settings).Execute()
