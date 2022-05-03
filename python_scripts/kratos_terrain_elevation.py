import KratosMultiphysics 
import KratosMultiphysics.KratosUnittest as KratosUnittest
#from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#                 3. THIRD MODULE OF KRATOS GEOMETRY MODELLING FOR TERRAIN MESHER APPLICATION 
# 
#                 The aim of this class is to elevate  2d contour mesh using a user defined raster file of the estudy zone. 
#------------------------------------------------------------------------------------------------------------------------------------------------------




class TerrainElevationFromRaster():
    def __init__(self,model,settings,BoundingBox,floor_identification_model):
        print("TerrainElevationFromRaster class constructor is called ")
        self.gmsh_kratos_format=settings["output_gmsh_2d_format"].GetString()
        self.mdpa_file=settings["file_name"].GetString()+"_2d"
        self.bounding_box=BoundingBox
        self.raster_file_name=settings["raster_file_name"].GetString()
        self.model_part=settings["floor_model_name"].GetString()
        self.main_model_part=settings["main_submodel"].GetString()
        self.model=model
        self.floor_property=floor_identification_model




    def Execute(self):
        print("Kratos Mapping tool Module is initialized")
        self.ReadingGmshMdpaToKratos()
        print("Two 2D not elevated mesh ir read")
        self.ReadingElevationRasterFile()
        print("Elevation raster file is read  mesh ir read")
        self.CratingGmshContourSubmodelPart()
        print("gmsh contour submodel parts are been defined")
        self.GeoprocessingRasterSubmodelPart()
        print("gmsh contour submodel parts are been defined")
        self.GmshContourElevation()    
    
    def ReadingGmshMdpaToKratos(self):
        
        self.ContouringModelPart=self.model.CreateModelPart("Contour")
        self.ContouringModelPart.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
        self.ContouringModelPart.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_DISPLACEMENT)
        self.ContouringModelPart.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_REACTION)
        self.ContouringModelPart.AddProperties(KratosMultiphysics.Properties(0))
        input_filename = self.mdpa_file
        reorder = False
        reorder_consecutive = False
        import_flags = KratosMultiphysics.ModelPartIO.READ
        import_flags = KratosMultiphysics.ModelPartIO.SKIP_TIMER|import_flags
        import_flags = KratosMultiphysics.ModelPartIO.IGNORE_VARIABLES_ERROR|import_flags

        if reorder_consecutive:
            KratosMultiphysics.ReorderConsecutiveModelPartIO(input_filename, import_flags).ReadModelPart(self.ContouringModelPart)
        else:
            KratosMultiphysics.ModelPartIO(input_filename, import_flags).ReadModelPart(self.ContouringModelPart)

        if reorder:
            tmp = KratosMultiphysics.Parameters("{}")
            KratosMultiphysics.ReorderAndOptimizeModelPartProcess(self.ContouringModelPart, tmp).Execute()

    def CratingGmshContourSubmodelPart(self):
        Submodel=self.ContouringModelPart.CreateSubModelPart(self.model_part)
        ElementsIdentities=[]
        Nodesidentities=[]
        for element in self.ContouringModelPart.Elements:
            if element.GetValue(KratosMultiphysics.ACTIVATION_LEVEL) == self.floor_property:    
                ElementsIdentities.append(element.Id)
                geom=element.GetGeometry()
                nodesid=[]
                element.Set(KratosMultiphysics.TO_ERASE)
                
                for i in range(geom.PointsNumber()):
                    node=geom[i]
                    Nodesidentities.append(node.Id)
                    nodesid.append(node.Id)
        Submodel.AddNodes(Nodesidentities)
        Submodel.AddElements(ElementsIdentities)   

                    
        Prop1=KratosMultiphysics.Properties(1)   

    def ReadingElevationRasterFile(self):
        xyz=open(self.raster_file_name,'r')
        xyz.readline()
        self.x_raster=[]
        self.y_raster=[]
        

        self.z_raster=[]
        for line in xyz:
            x,y,z =line.split()
            self.x_raster.append(float(x))
            self.y_raster.append(float(y))
            self.z_raster.append(float(z))
        
        MaxZ=max(self.z_raster)
        MinZ=min(self.z_raster)
        self.DeltaZ=MaxZ-MinZ
        #TODO: A function in gmsh with the boundingbox call
        MinX=self.bounding_box[1][0]
        MinY=self.bounding_box[1][1]
        for i in range(len(self.x_raster)):
            self.x_raster[i] = self.x_raster[i] - MinX
            self.y_raster[i] = self.y_raster[i] - MinY
            self.z_raster[i] = self.z_raster[i] - MinZ
        self.MaxZ=max(self.z_raster)
    def GetMaximumFloorElevation(self):
        return self.MaxZ
    def GeoprocessingRasterSubmodelPart(self):
        
        
        self.Geoprocessing_raster=self.model.CreateModelPart("GeoprocessingRaster")
        raster_mesh= self.Geoprocessing_raster.CreateSubModelPart("raster")
        mysubmodel=self.model 
        raster_mesh.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_DISPLACEMENT_Z)
        raster_mesh.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_DISPLACEMENT_Z)
        for i in range(int(len(self.x_raster))):
            raster_mesh.CreateNewNode(i + 1, self.x_raster[i], self.y_raster[i
            ],  0)
        KratosMultiphysics.CreateTriangleMeshFromNodes.CreateTriangleMeshFromNodes(raster_mesh)
        for node in raster_mesh.Nodes:
            node.SetSolutionStepValue(KratosMultiphysics.MESH_DISPLACEMENT_Z,0,self.z_raster[node.Id-1])

    def GmshContourElevation(self):
        mapper_project_parameters = KratosMultiphysics.Parameters("""{
            "mapper_type" : "",
            "interface_submodel_part_origin" : "",
            "interface_submodel_part_destination" : ""
                }""")
        mapper_project_parameters["mapper_type"].SetString("nearest_neighbor")
        mapper_project_parameters["interface_submodel_part_origin"].SetString("raster")
        mapper_project_parameters["interface_submodel_part_destination"].SetString(self.model_part)      
        # for node in self.ContouringModelPart.GetSubModelPart(self.model_part).Nodes:
        interface_mapper = KratosMapping.MapperFactory.CreateMapper(self.Geoprocessing_raster, self.ContouringModelPart, mapper_project_parameters)
        interface_mapper.Map(KratosMultiphysics.MESH_DISPLACEMENT_Z, KratosMultiphysics.MESH_DISPLACEMENT_Z)

            # Elevation= node.GetSolutionStepValue(KratosMultiphysics.MESH_DISPLACEMENT_Z)
            # node.Z0=Elevation-self.DeltaZ
            # node.Z=Elevation-self.DeltaZ
        for node in self.ContouringModelPart.GetSubModelPart(self.model_part).Nodes:

            Elevation= node.GetSolutionStepValue(KratosMultiphysics.MESH_DISPLACEMENT_Z)
            node.Z0=Elevation
            node.Z=Elevation
    
    
        gid_output = GiDOutputProcess(self.ContouringModelPart.GetSubModelPart(self.model_part), 
                                            "mallagidmappero",
                                            KratosMultiphysics.Parameters("""
                                                {
                                                    "result_file_configuration" : {
                                                        "gidpost_flags": {
                                                            "GiDPostMode": "GiD_PostAscii",
                                                            "WriteDeformedMeshFlag": "WriteUndeformed",
                                                            "WriteConditionsFlag": "WriteConditions",
                                                            "MultiFileFlag": "SingleFile"
                                                        },
                                                        "file_label": "time",
                                                        "output_control_type": "step",
                                                        "output_interval": 1.0,
                                                        "body_output": true,
                                                        "node_output": false,
                                                        "skin_output": false,
                                                        "plane_output": [],
                                                        "nodal_results"       : ["MESH_DISPLACEMENT_Z"],
                                                        "nodal_nonhistorical_results": [],
                                                        "nodal_flags_results": [],
                                                        "gauss_point_results": [],
                                                        "additional_list_files": []
                                                    }
                                                }
                                                """)
                                            )
            
        gid_output.ExecuteInitialize()
        gid_output.ExecuteBeforeSolutionLoop()
        gid_output.ExecuteInitializeSolutionStep()
        gid_output.PrintOutput()
        gid_output.ExecuteFinalizeSolutionStep()
        gid_output.ExecuteFinalize()
  
