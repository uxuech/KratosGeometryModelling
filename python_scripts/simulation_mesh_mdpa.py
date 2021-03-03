class SimulationMeshMdpa():
    def __init__(self,mdpa_file_name):
        self.file_name=mdpa_file_name
    def __ReadingMdpaFile(self):
        model= KM.Model()
        ColorModelPart=model.CreateModelPart("Colors")
        ColorModelPart.ProcessInfo[KM.DOMAIN_SIZE] = 3
        ColorModelPart.AddNodalSolutionStepVariable(KM.MESH_DISPLACEMENT)
        ColorModelPart.AddNodalSolutionStepVariable(KM.MESH_REACTION)
        ColorModelPart.AddProperties(KM.Properties(0))
        input_filename = "test_volume_good"
        reorder = False
        reorder_consecutive = False
        import_flags = KM.ModelPartIO.READ
        import_flags = KM.ModelPartIO.SKIP_TIMER|import_flags
        import_flags = KM.ModelPartIO.IGNORE_VARIABLES_ERROR|import_flags

        if reorder_consecutive:
            KM.ReorderConsecutiveModelPartIO(input_filename, import_flags).ReadModelPart(ColorModelPart)
        else:
            KM.ModelPartIO(input_filename, import_flags).ReadModelPart(ColorModelPart)

        if reorder:
            tmp = KM.Parameters("{}")
        KM.ReorderAndOptimizeModelPartProcess(ColorModelPart, tmp).Execute()
    def __MdpaTwoFluidSimulation(self):

        ErasedElements=[]
        for Bound in BoundariesSurface:
            print(Bound[1])
            Submodel=ColorModelPart.CreateSubModelPart(Bound[1])
            ElementsIdentities=[]
            Nodesidentities=[]
            for element in ColorModelPart.Elements:
                if element.GetValue(KM.ACTIVATION_LEVEL) == Bound[0]:    
                    ElementsIdentities.append(element.Id)
                    geom=element.GetGeometry()
                    nodesid=[]
                    element.Set(KM.TO_ERASE)
                    ErasedElements.append(element.Id)
                    for i in range(geom.PointsNumber()):
                        node=geom[i]
                        Nodesidentities.append(node.Id)
                        nodesid.append(node.Id)
                    Submodel.AddNodes(nodesid) 
                    BoundaryCondition = Submodel.CreateNewCondition("SurfaceCondition3D3N", element.Id, nodesid, Submodel.GetProperties()[0])
                    BoundaryCondition.SetValue(KM.ACTIVATION_LEVEL,element.GetValue(KM.ACTIVATION_LEVEL))
                    
            print(Submodel)

        print(ContouringModelPart)
        Prop1=KM.Properties(1)    
        for bodies in Body: 
            print(bodies[1])
            Submodel=ColorModelPart.CreateSubModelPart(bodies[1])
            Submodel.AddProperties(Prop1)
            ElementsIdentities=[]
            Triangleidentities=[]
            for element in ColorModelPart.Elements:
                if element.GetValue(KM.ACTIVATION_LEVEL) == bodies[0]: 
                    element.Properties=Prop1   
                    ElementsIdentities.append(element.Id)
                    geom=element.GetGeometry()
                    for i in range(geom.PointsNumber()):
                        triangle=geom[i]
                        # print("AQUIIIIIIIIIIIIIII")
                        # print(triangle)
                        Triangleidentities.append(triangle.Id)
                        
            Submodel.AddNodes(Triangleidentities)        
            Submodel.AddElements(ElementsIdentities)
            print(Submodel)
        ColorModelPart.RemoveElements(KM.TO_ERASE)  
        name_out_file="Urederra_elevation_meshing"
        KM.ModelPartIO(name_out_file, KM.IO.WRITE).WriteModelPart(ColorModelPart)
