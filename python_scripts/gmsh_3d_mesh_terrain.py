class Gmsh3dMeshTerrain():
    #TODO: Pensar en como  vamos a leer kratos_desde ??
    def __init__(self,elevation,mesh_size_3d):
        self.elevation=elevation
        self.mesh_size=mesh_size_3d
    
    def __ReadingKratosTerrainMeshGmsh(self):

    def __TopSurfaceDefinition(self):

    def __AuxiliarySkinTriangulationGmsh(self,TopNodesbyBoundary,FloorNodesbyBoundary,BoundaryDictionary): 
        connectivities_by_boundary={}
        print(BoundaryDictionary)
        for boundary in BoundaryDictionary:
            print(boundary)
            bound=boundary.tolist()[0]
            connectivities=[]
            for j in range(len(TopNodesbyBoundary[bound])-1):
                # PRIMER TRIANGULO DEL SEGMENTO (se insertar todos en una unica lista para aña)
                connectivities.append(TopNodesbyBoundary[bound][j])
                connectivities.append(BoundaryNodesIds_newfloor[bound][j])
                connectivities.append(BoundaryNodesIds_newfloor[bound][j+1])

                #SEGUNDO TRIANGULO DEL SEGMENTO
                connectivities.append(TopNodesbyBoundary[bound][j])
                connectivities.append(BoundaryNodesIds_newfloor[bound][j+1])
                connectivities.append(TopNodesbyBoundary[bound][j+1])
            connectivities_by_boundary[bound]=connectivities
        return connectivities_by_boundary


    def __Gmsh3dDiscreteMesh(self):
    ConectivitiesByBoundary=SkinTriangulationGmsh(BoundaryNodesIds_Top,BoundaryNodesIds_newfloor,BoundaryDictionary)

        FloorPoints=NewFloor_SurfaceDataBase.ExternalPointEntity()
        TopPoints=TopSurfaceDataBase.ExternalPointEntity()
        print(FloorPoints)
        print(TopPoints)

        # IdsLineDict={}
        control_check=[]
        InitialLines=[]
        for i in range(len( BoundaryDictionary)):
            Bound=BoundaryDictionary[i].tolist()[0]
            print(BoundaryNodesIds_newfloor[Bound][0],BoundaryNodesIds_Top[Bound][0])
            print(FloorPoints[Bound][0],TopPoints[Bound][0])
            initialline=gmsh.model.addDiscreteEntity(1,-1,[FloorPoints[Bound][0],TopPoints[Bound][0]])
            gmsh.model.mesh.addElementsByType(initialline, 1, [],[BoundaryNodesIds_newfloor[Bound][0],BoundaryNodesIds_Top[Bound][0]])
            # finallines=gmsh.model.addDiscreteEntity(1,-1,[TopPoints[Bound][1],FloorPoints[Bound][1]])
            # gmsh.model.mesh.addElementsByType(finallines, 1, [],[BoundaryNodesIds_newfloor[Bound][-1],BoundaryNodesIds_Top[Bound][-1]])
            Idwithpoint=[initialline,FloorPoints[Bound][0]]
            InitialLines.append(initialline)
            control_check.append(Idwithpoint)

        endlines=[]
        for i in range (len(BoundaryDictionary)):
            Bound=BoundaryDictionary[i].tolist()[0]
            for element in control_check:
                if FloorPoints[Bound][1] == element[1]:
                    endlines.append(element[0])
        print(InitialLines)
        print(endlines)

        FloorPhysical=gmsh.model.addPhysicalGroup(2,[EntityFloor])
        gmsh.model.setPhysicalName(2,FloorPhysical,"Floor")

        TopPhysical=gmsh.model.addPhysicalGroup(2,[topSurface_IdentitieId])
        gmsh.model.setPhysicalName(2,TopPhysical,"Top")

        test=[]
        for i in range(len( BoundaryDictionary)):
            Bound=BoundaryDictionary[i].tolist()[0]
            initial=InitialLines[i]
            Topline=linesIdsTop[i]
            final=endlines[i]
            FloorLine= Bound
            SurfaceSkin=gmsh.model.addDiscreteEntity(2,-1,[initial,final,Topline,FloorLine])
            gmsh.model.mesh.addElementsByType(SurfaceSkin,2,[],ConectivitiesByBoundary[Bound])
            AssigningiBoundary=gmsh.model.addPhysicalGroup(2,[SurfaceSkin])
            gmsh.model.setPhysicalName(2,AssigningiBoundary,Boundariestype[i])
            gmsh.model.mesh.reclassifyNodes()
            gmsh.model.mesh.createGeometry()
            gmsh.model.geo.removeAllDuplicates()
            test.append(AssigningiBoundary)



                
        surfaces = gmsh.model.getEntities(2)
        gmsh.model.geo.synchronize()
        loopSurface = gmsh.model.geo.addSurfaceLoop([surfaces[i][1] for i in range(len(surfaces))])

        Volume=gmsh.model.geo.addVolume([loopSurface])
        gmsh.model.geo.synchronize()
        VolumePhysical=gmsh.model.addPhysicalGroup(3,[Volume])
        gmsh.model.setPhysicalName(3,VolumePhysical,"Fluid")
        gmsh.model.getPhysicalName(3,Volume)
        gmsh.model.geo.removeAllDuplicates()
        print(gmsh.model.getEntities())

        AllEntitiesSurface=gmsh.model.getEntities(2)
        AllentitiesVolumes=gmsh.model.getEntities(3)
        print(AllentitiesVolumes)
        Boundaries=DictionaryForSubModelPart(AllEntitiesSurface,AllentitiesVolumes)
        print(Boundaries)


    def __ExportingMeshToMdpa(self):
        gmsh.write("VolumeMeshUrederra.vtk")
        meshing=meshio.read("VolumeMeshUrederra.vtk")
        meshio.mdpa.write("test_volume.mdpa", meshing)
        gmsh.clear()
        gmsh.finalize()
        toedit_mdpa=open("test_volume.mdpa","r")
        edited_mdpa = open("test_volume_good.mdpa", 'w')
        checkWords = ("Begin Elements Triangle3D3","Begin Elements Tetrahedra3D4","Begin ElementalData CellEntityIds","End ElementalData CellEntityIds")
        repWords = ("Begin Elements Element3D3N","Begin Elements Element3D4N","Begin ElementalData ACTIVATION_LEVEL","End ElementalData")

        for line in toedit_mdpa:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            edited_mdpa.write(line)
        toedit_mdpa.close()
        edited_mdpa.close()
        import KratosMultiphysics as KM
        import KratosMultiphysics.KratosUnittest as KratosUnittest
        #from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
        from KratosMultiphysics.gid_output_process import GiDOutputProcess
        import KratosMultiphysics.MappingApplication as KratosMapping
        from KratosMultiphysics.MappingApplication import python_mapper_factory
        from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis
        import meshio
        import numpy as np
        # RELACIONAR LAS BOUNDARIES USUARIO Y LAS ASIGNADAS POR EL GMSH ( EXTRAER LA INFORMACION DEL OTRO SCRIPT --DE MOMENTO AUXILIAR ESTA LISTA DE LISTAS)
        BoundariesSurface=Boundaries[2]
        Body=Boundaries[3]

    def Execute(self):
        self.__Gmsh3dDiscreteMesh()
        self.__ExportingMeshToMdpa()
        self.__AuxiliarySkinTriangulationGmsh()
        self.__ReadingKratosTerrainMeshGmsh()
        self.__TopSurfaceDefinition()