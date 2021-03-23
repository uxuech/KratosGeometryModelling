class TerrainElevationFromRaster():
    def __init__(self,MdpaFile,ConditionName,RasterFIleName):
        self.mdpa_file=MdpaFile
        self.conditon_name=ConditionName
        self.raster_file_name=RasterFIleName
    def ReadingGmshMdpaToKratos(self):
        model= KM.Model()

        ContouringModelPart=model.CreateModelPart("ContouringModel")
        ContouringModelPart.ProcessInfo[KM.DOMAIN_SIZE] = 3
        ContouringModelPart.AddNodalSolutionStepVariable(KM.MESH_DISPLACEMENT)
        ContouringModelPart.AddNodalSolutionStepVariable(KM.MESH_REACTION)
        ContouringModelPart.AddProperties(KM.Properties(0))
        input_filename = "test_good"
        reorder = False
        reorder_consecutive = False
        import_flags = KM.ModelPartIO.READ
        import_flags = KM.ModelPartIO.SKIP_TIMER|import_flags
        import_flags = KM.ModelPartIO.IGNORE_VARIABLES_ERROR|import_flags

        if reorder_consecutive:
            KM.ReorderConsecutiveModelPartIO(input_filename, import_flags).ReadModelPart(ContouringModelPart)
        else:
            KM.ModelPartIO(input_filename, import_flags).ReadModelPart(ContouringModelPart)

        if reorder:
            tmp = KM.Parameters("{}")
            KM.ReorderAndOptimizeModelPartProcess(ContouringModelPart, tmp).Execute()
    def CratingGmshContourSubmodelPart(self):
        Submodel=ContouringModelPart.CreateSubModelPart(self.conditon_name)
        ElementsIdentities=[]
        Nodesidentities=[]
        for element in ContouringModelPart.Elements:
            if element.GetValue(KM.ACTIVATION_LEVEL) == 5:    
                ElementsIdentities.append(element.Id)
                geom=element.GetGeometry()
                nodesid=[]
                element.Set(KM.TO_ERASE)
                
                for i in range(geom.PointsNumber()):
                    node=geom[i]
                    Nodesidentities.append(node.Id)
                    nodesid.append(node.Id)
        Submodel.AddNodes(Nodesidentities)
        Submodel.AddElements(ElementsIdentities)   

                    
        Prop1=KM.Properties(1)   

    def ReadingElevationRasterFile(self):
        xyz=open("urederra25buffer.xyz",'r')
        xyz.readline()
        self.x_raster=[]
        self.y_raster=[]
        # ELEVATION=(DENSITY)
        self.z_raster=[]
        for line in xyz:
            x,y,z =line.split()
            x_raster.append(float(x))
            y_raster.append(float(y))
            z_raster.append(float(z))
        MaxZ=max(z_raster)
        MinZ=min(z_raster)
        DeltaZ=MaxZ - MinZ
        #TODO: A function in gmsh with the boundingbox call
        MinX=571567.272
        MinY=4734408.251
        for i in range(len(x_raster)):
            x_raster[i] = x_raster[i] - MinX
            y_raster[i] = y_raster[i] - MinY
            z_raster[i] = z_raster[i] - MinZ

    def GeoprocessingRasterSubmodelPart(self):
        Geoprocessing_raster=model.CreateModelPart("GeoprocessingRaster")
        raster_mesh= Geoprocessing_raster.CreateSubModelPart("raster")
        mysubmodel=model 
        raster_mesh.AddNodalSolutionStepVariable(KM.MESH_DISPLACEMENT_Z)
        raster_mesh.AddNodalSolutionStepVariable(KM.MESH_DISPLACEMENT_Z)
        for i in range(int(len(self.x_raster))):
            raster_mesh.CreateNewNode(i + 1, self.x_raster[i], self.y_raster[i
            ],  0)
        KM.CreateTriangleMeshFromNodes.CreateTriangleMeshFromNodes(raster_mesh)
        for node in raster_mesh.Nodes:
            node.SetSolutionStepValue(KM.MESH_DISPLACEMENT_Z,0,self.z_raster[node.Id-1])

    def GmshContourElevation(self):
        mapper_project_parameters = KM.Parameters("""{
            "mapper_type" : "",
            "interface_submodel_part_origin" : "",
            "interface_submodel_part_destination" : ""
                }""")
        mapper_project_parameters["mapper_type"].SetString("nearest_element")
        mapper_project_parameters["interface_submodel_part_origin"].SetString("raster")
        mapper_project_parameters["interface_submodel_part_destination"].SetString("Floor")      
        for node in ContouringModelPart.GetSubModelPart("Floor").Nodes:
            interface_mapper = KratosMapping.MapperFactory.CreateMapper(Geoprocessing_raster, ContouringModelPart, mapper_project_parameters)
            interface_mapper.Map(KM.MESH_DISPLACEMENT_Z, KM.MESH_DISPLACEMENT_Z)

            Elevation= node.GetSolutionStepValue(KM.MESH_DISPLACEMENT_Z)
            node.Z0=Elevation-DeltaZ
            node.Z=Elevation-DeltaZ