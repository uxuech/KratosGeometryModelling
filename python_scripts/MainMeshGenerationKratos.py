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
from simulation_mesh_mdpa import SimulationMeshMdpa
import KratosMultiphysics 
import KratosMultiphysics.KratosUnittest as KratosUnittest
#from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis
# from JoininModelPart import JoiningModelParts

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


with open("UserProperties.json",'r') as parameter_file:
    default_settings = KratosMultiphysics.Parameters(parameter_file.read())    
  
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
Floor_identification=Contour2dMesher.GetActivitatioLevelFloor()
# Terrain elevation using mapping 
TerrainMapping=TerrainElevationFromRaster(model,default_settings,BoundingBox,Floor_identification)
TerrainMapping.Execute()
maximum_terrain_elevation=TerrainMapping.GetMaximumFloorElevation()
# Meshing model in volume terms
VolumeMesh= Gmsh3dMeshTerrain(model,default_settings,TotalBoundariesNames,TotalNodesBoundaryId,Total_external_points,Boundary,Gmsh_geometry
,maximum_terrain_elevation)
VolumeMesh.Execute()
KratosColors=VolumeMesh.GetKratosColorsIdentifiers()
# Assigning colors to meshing surface. w
ColorAssignation=SimulationMeshMdpa(default_settings,KratosColors)
ColorAssignation.Execute()
# Joinining ModelParts 
# JoinSlipBoundaries=JoiningModelParts(model,default_settings)
# JoinSlipBoundaries.Execute()



