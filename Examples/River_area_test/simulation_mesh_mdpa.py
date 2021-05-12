
import KratosMultiphysics 
import os 
import json 
from KratosMultiphysics.sub_model_part_entities_boolean_operation_process import  SubModelPartEntitiesBooleanOperationProcess
class SimulationMeshMdpa():
    def __init__(self,settings,KratosColors):
        self.file_name=settings["file_name"].GetString()
        self.outputfile_2d=settings["file_name"].GetString()
        self.kratos_color_identifiers=KratosColors

        
        #Decirle A Ruben si se uede hacer esto 
        # self.joined_model_part_name=settings["joined_model_name"].GetLIsta(ruen)
        self.wall_model_parts=settings["Slip_Boundaries"]
        # self.wall_model_parts=["Walls1","Walls2","Top","Floor"]
        self.condition=settings["condition"].GetBool()
        self.nodes=settings["nodes"].GetBool()
        self.joined_model_part_name=settings["join_model_name"].GetString()
        self.join_model_part=settings["join_models"].GetBool()
        

    def __ReadingMdpaFile(self):
        self.model= KratosMultiphysics.Model()
        self.ColorModelPart=self.model.CreateModelPart("Colors")
        self.ColorModelPart.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
        self.ColorModelPart.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_DISPLACEMENT)
        self.ColorModelPart.AddNodalSolutionStepVariable(KratosMultiphysics.MESH_REACTION)
        self.ColorModelPart.AddProperties(KratosMultiphysics.Properties(0))
        input_filename = self.file_name+"_3d"
        reorder = False
        reorder_consecutive = False
        import_flags = KratosMultiphysics.ModelPartIO.READ
        import_flags = KratosMultiphysics.ModelPartIO.SKIP_TIMER|import_flags
        import_flags = KratosMultiphysics.ModelPartIO.IGNORE_VARIABLES_ERROR|import_flags

        if reorder_consecutive:
            KratosMultiphysics.ReorderConsecutiveModelPartIO(input_filename, import_flags).ReadModelPart(self.ColorModelPart)
        else:
            KratosMultiphysics.ModelPartIO(input_filename, import_flags).ReadModelPart(self.ColorModelPart)

        if reorder:
            tmp = KratosMultiphysics.Parameters("{}")
            KratosMultiphysics.ReorderAndOptimizeModelPartProcess(self.ColorModelPart, tmp).Execute()
        if os.path.exists(self.file_name+"_3d.mdpa"):
            os.remove(self.file_name+"_3d.mdpa")
    def __MdpaTwoFluidSimulation(self):

        ErasedElements=[]
        for surface in self.kratos_color_identifiers[2]:
            
            Submodel=self.ColorModelPart.CreateSubModelPart(surface[1])
            ElementsIdentities=[]
            Nodesidentities=[]
            for element in self.ColorModelPart.Elements:
                if element.GetValue(KratosMultiphysics.ACTIVATION_LEVEL) == surface[0]:    
                    ElementsIdentities.append(element.Id)
                    geom=element.GetGeometry()
                    nodesid=[]
                    element.Set(KratosMultiphysics.TO_ERASE)
                    ErasedElements.append(element.Id)
                    for i in range(geom.PointsNumber()):
                        node=geom[i]
                        Nodesidentities.append(node.Id)
                        nodesid.append(node.Id)
                    Submodel.AddNodes(nodesid) 
                    BoundaryCondition = Submodel.CreateNewCondition("SurfaceCondition3D3N", element.Id, nodesid, Submodel.GetProperties()[0])
                    BoundaryCondition.SetValue(KratosMultiphysics.ACTIVATION_LEVEL,element.GetValue(KratosMultiphysics.ACTIVATION_LEVEL))
        Prop1=KratosMultiphysics.Properties(1)    
        for volume in  self.kratos_color_identifiers[3]: 
            print(volume[1])
            Submodel=self.ColorModelPart.CreateSubModelPart(volume[1])
            Submodel.AddProperties(Prop1)
            ElementsIdentities=[]
            Triangleidentities=[]
            for element in self.ColorModelPart.Elements:
                if element.GetValue(KratosMultiphysics.ACTIVATION_LEVEL) == volume[0]: 
                    element.Properties=Prop1   
                    ElementsIdentities.append(element.Id)
                    geom=element.GetGeometry()
                    for i in range(geom.PointsNumber()):
                        triangle=geom[i]

                        Triangleidentities.append(triangle.Id)
                        
            Submodel.AddNodes(Triangleidentities)        
            Submodel.AddElements(ElementsIdentities)
            print(Submodel)
        self.ColorModelPart.RemoveElements(KratosMultiphysics.TO_ERASE)  

    def __WriteFinalMdpa(self):
        name_out_file=self.file_name+"_3d"
        KratosMultiphysics.ModelPartIO(name_out_file, KratosMultiphysics.IO.WRITE).WriteModelPart(self.ColorModelPart)
        if not self.outputfile_2d :
            os.remove(self.file_name+"_2d.mdpa")
            os.remove(self.file_name+"_2d.vtk")
            os.remove(self.file_name+"_3d.vtk")
    


    def __CreateJoinedEmptyModelPart(self):
        self.join_sub_model=self.ColorModelPart.CreateSubModelPart(self.joined_model_part_name)

        

    def __WriteFinalMdpaJoined(self):
        name_out_file=self.file_name+"_3d_joined"
        KratosMultiphysics.ModelPartIO(name_out_file, KratosMultiphysics.IO.WRITE).WriteModelPart(self.ColorModelPart)
    
    def __JoiningSlipConditionModelParts(self):

        json_file=open("Joiningmodels.json", "r")
        json_object = json.load(json_file)
        json_file.close()
        for i  in range(self.wall_model_parts.size()):
            self.model_part_to_join=self.wall_model_parts[i].GetString()
            
            json_object["first_model_part_name"]= "Colors.SLIPBC"
            json_object["second_model_part_name"]=self.model_part_to_join
            json_object["result_model_part_name"]= "Colors.SLIPBC"
            if self.nodes:
                json_object["entity_type"]="Nodes"
                json_file=open("Joiningmodels.json", "w")
                json.dump(json_object, json_file)
                json_file.close()
                with open("Joiningmodels.json",'r') as settings_file:
                    parameters = KratosMultiphysics.Parameters(settings_file.read())
                    SubModelPartEntitiesBooleanOperationProcess(self.model,parameters)
                
            if self.condition:
                json_object["entity_type"]="Conditions" 
                json_file=open("Joiningmodels.json", "w")
                json.dump(json_object, json_file)
                json_file.close()
                with open("Joiningmodels.json",'r') as parameter_file:
                    parameters = KratosMultiphysics.Parameters(parameter_file.read())
                    SubModelPartEntitiesBooleanOperationProcess(self.model,parameters)
 
    def Execute(self):
        self.__ReadingMdpaFile()
        self.__MdpaTwoFluidSimulation()
        if self.join_model_part:
            print("we are here")
            # self.__ReadingInputMdpa()
            self.__CreateJoinedEmptyModelPart()
            self.__JoiningSlipConditionModelParts()
            self.__WriteFinalMdpaJoined()
        else:
            warning_msg="WARNING:Not Joined slip boundary condition may add uncertainty to the problem"
            print(warning_msg)
            self.__WriteFinalMdpa()
