import shapefile    
import gmsh
import sys
import meshio


# importing external classes in order to build tridimensional terrain mesh automatycally 
from contour_input_output import ContourInputOutput
from gmsh_contour_2D_mesh import GmshContour2dMeshGenerator
from gmsh_3d_mesh_terrain import Gmsh3dMeshTerrain
from kratos_terrain_elevation import TerrainElevationFromRaster
from simulation_mesh_mdpa import SimulationMeshMdpa
import KratosMultiphysics 
import KratosMultiphysics.KratosUnittest as KratosUnittest
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis

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
# Terrain elevation using mapping 
TerrainMapping=TerrainElevationFromRaster(model,default_settings,BoundingBox)
TerrainMapping.Execute()
maximum_terrain_elevation=TerrainMapping.GetMaximumFloorElevation()
# Meshing model in volume terms
VolumeMesh= Gmsh3dMeshTerrain(model,default_settings,TotalBoundariesNames,TotalNodesBoundaryId,Total_external_points,Boundary,Gmsh_geometry
,maximum_terrain_elevation)
VolumeMesh.Execute()
KratosColors=VolumeMesh.GetKratosColorsIdentifiers()
# Assigning colors to meshing surface.
ColorAssignation=SimulationMeshMdpa(default_settings,KratosColors)
ColorAssignation.Execute()


