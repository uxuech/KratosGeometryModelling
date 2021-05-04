import shapefile    
import gmsh
import sys
import meshio

# importing external classes in order to build tridimensional terrain mesh automatycally 
from contour_input_output import ContourInputOutput
from gmsh_contour_2D_mesh import GmshContour2dMeshGenerator
# from simulation_mesh_medpa import SimulationMeshMdpa
from gmsh_3d_mesh_terrain import Gmsh3dMeshTerrain
from kratos_terrain_elevation import TerrainElevationFromRaster
import KratosMultiphysics 
import KratosMultiphysics.KratosUnittest as KratosUnittest
#from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis
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
        	"file_name":"TestGood",
        	"round_coordinates": true,
        	"file_format":".shp",
        	"move_to_origen":true,
        	"tolerance_repeated_points":1e-5,
			"mesh_size":5,
			"output_file_name":"urederra_2d.vtk",
			"output_file_mdpa":"urederra_2d.mdpa",
			"kratos_file_name": "urederra_contour.mdpa",
			"kratos_file_name3":"urederra_contour_kratos.mdpa",
			"kratos_file_name2":"urederra_contour_kratos",
			"raster_file_name": "urederra25buffer.xyz",
			"main_submodel":"Contour",
			"floor_model_name": "Floor",
			"top_model_name": "Top",
			"3d_model_elevation":100,
			"3d_mesh_size":5
        }""")

    
model = KratosMultiphysics.Model()

# PreProcessingGeometry
PreparingGeometry=ContourInputOutput(default_settings)
PreparingGeometry.Execute()
Gmsh_geometry=PreparingGeometry.GetPolylinesGmshContourDic()
Boundary=PreparingGeometry.GetContourBoundaryName()
BoundingBox=PreparingGeometry.ContourBoundingBox()
# Geometry ready in order to initialize 2d contoru mesh 
Contour2dMesher=GmshContour2dMeshGenerator(default_settings,Boundary,Gmsh_geometry)
Contour2dMesher.Execute()
TotalBoundariesNames=Contour2dMesher.GetTotalBoundariesName()
TotalNodesBoundaryId=Contour2dMesher.GetTotalNodesBoundaryId()

Total_external_points=Contour2dMesher.GetTotalExternalPoints()
# Terrain elevation using mapping 
TerrainMapping=TerrainElevationFromRaster(model,default_settings,BoundingBox)
TerrainMapping.Execute()
# Meshing model in volume terms
VolumeMesh= Gmsh3dMeshTerrain(model,default_settings,TotalBoundariesNames,TotalNodesBoundaryId,Total_external_points,Boundary,Gmsh_geometry)
VolumeMesh.Execute()
# TerrainElevationFromRaster(default_settings).Execute()
# Gmsh3dMeshTerrain(default_settings).Execute()
