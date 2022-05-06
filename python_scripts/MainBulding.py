import shapefile
import gmsh
import sys
import meshio
# importing external classes in order to build tridimensional terrain mesh automatycally
from building import BuildingMeshTool
#from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
import KratosMultiphysics
import KratosMultiphysics.KratosUnittest as KratosUnittest
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis


with open("UserProperties.json", 'r') as parameter_file:
    default_settings = KratosMultiphysics.Parameters(parameter_file.read())

PreparingBuldingGeometry = BuildingMeshTool(default_settings)
PreparingBuldingGeometry.Execute()
