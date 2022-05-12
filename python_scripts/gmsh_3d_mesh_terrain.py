
import KratosMultiphysics 
import KratosMultiphysics.KratosUnittest as KratosUnittest
#from KratosMultiphysics.CoSimulationApplication.utilities import model_part_utilities
from KratosMultiphysics.gid_output_process import GiDOutputProcess
from KratosMultiphysics.vtk_output_process import VtkOutputProcess
import KratosMultiphysics.MappingApplication as KratosMapping
from KratosMultiphysics.MappingApplication import python_mapper_factory
from KratosMultiphysics.MeshMovingApplication.mesh_moving_analysis import MeshMovingAnalysis
import shapefile    
import gmsh
import sys
import meshio
import os
class Gmsh3dMeshTerrain():
    #TODO: Pensar en como  vamos a leer kratos_desde ??
    def __init__(self,model,settings,TotalBoundariesNames,TotalNodesBoundaryId,Total_external_points,boundary_type,Gmsh_geometry,maximum_terrain_elevation):
        # Initializing gmsh model once again. TODO: El nombre del modelo de gmsh es necesario ofrecerlo al usuario o algo interno_ RUBEN
        gmsh.initialize()
        gmsh.model.add("new_model")

        self.contour_submodel_part=settings["main_submodel"].GetString()
        self.floor_model_part=settings["floor_model_name"].GetString()
        self.top_model_part_name=settings["top_model_name"].GetString()
        self.elevation=settings["3d_model_elevation"].GetDouble()
        self.mesh_size=settings["3d_mesh_size"].GetDouble()
        #TODO: maybe this variable is twice repeated CHECK ASAP
        self.total_boundaries_names=TotalBoundariesNames
        self.boundary_user_name=boundary_type
        self.boundary_nodes_id=TotalNodesBoundaryId
        self.total_external_points=Total_external_points
        self.boundary_user_name=boundary_type
        self.gmsh_geometry_dictionary=Gmsh_geometry
        self.file_name=settings["file_name"].GetString()
        self.maximum_terrain_elevation=maximum_terrain_elevation
        self.model=model

    def __ReadingKratosTerrainElevatedMeshGmsh(self):
        self.contour_model_part=self.model.GetModelPart(self.contour_submodel_part)
        self.elevated_mesh_model_part=self.contour_model_part.GetSubModelPart(self.floor_model_part)
        self.floor_surface_data_base=BoundaryNodalIdentification(self.total_boundaries_names,self.boundary_nodes_id,self.total_external_points)
        self.boundary_nodes_ids=self.floor_surface_data_base.NodesIdentitiesbyBoundary()
        self.boundary_gmsh_identifier=self.floor_surface_data_base.GetBoundaryNames()
        

    def __FromMeshToDiscretizatedFloorModel(self):

        self.nodes_inserted=[]
        self.coords=[]
        self.node_not_repeated=[]
        self.lines_discrete_entities=[]
        self.test=[]
        
        self.__DiscreteBoundaryEntitiesDefinition()
        self.__FloorNodesIdentification()
        self.__Floor1dElementsDefinition()
        self.__Floor2dElementsDefinition()
        self.__CreateFloorDiscreteGeometry()

    def __DiscreteBoundaryEntitiesDefinition(self):
        # This method redefines again 2d Contour  study case in a discrete way.
        for node in self.elevated_mesh_model_part.Nodes:
            self.test.append(node.Id)
        
        for boundary_list in self.boundary_gmsh_identifier:
            self.extracted_boundary_name=boundary_list.tolist()[0]
            self.nodes_storages=self.boundary_nodes_ids[self.extracted_boundary_name]
            self.point_entity=[]
            self.coordinates_point=[]
            # Nodal identification between Kratos node Id and Gmsh Id.
            # Boundary Nodes are identified in order to transform into geometric points.
            # Important not to add twice a discrete entity. 
            # Therefore the corner`s nodes corresponding to two boundary condition have to be defined once as a discrete entity
            # Here boundary points are defined 0D
            for node in self.elevated_mesh_model_part.Nodes:
                self.nodes_inserted.append(node.Id)
                self.cordinates=[node.X, node.Y, node.Z]
                
                self.coords.extend(self.cordinates)
                
                
                if node.Id == self.nodes_storages[0]:
                    if node.Id not in self.node_not_repeated:
                        gmsh.model.addDiscreteEntity(0, node.Id)
                        gmsh.model.setCoordinates(node.Id, node.X, node.Y, node.Z)
                        self.point_entity.append(node.Id)
                        self.node_not_repeated.append(node.Id)
                    else:
                        
                        self.point_entity.append(node.Id)
                        
                elif node.Id == self.nodes_storages[-1]:
                    if node.Id not in self.node_not_repeated:
                        gmsh.model.addDiscreteEntity(0, node.Id)
                        gmsh.model.setCoordinates(node.Id, node.X, node.Y, node.Z)
                        self.point_entity.append(node.Id)
                        self.node_not_repeated.append(node.Id)
                    else:
                        self.point_entity.append(node.Id)
            
            # Here boundary discrete lines are defined.1D
            line_dicrete_entity_id=gmsh.model.addDiscreteEntity(1, self.extracted_boundary_name, self.point_entity)
            self.lines_discrete_entities.append(line_dicrete_entity_id)
        # Here discrete floor contour is defined 2D
        self.entity_floor=gmsh.model.addDiscreteEntity(2, 1,self.lines_discrete_entities)
    def __FloorNodesIdentification(self):
        # Here all nodes generated from the previous gmsh model are added as a node entity,independently, where they are located.
        # Nodes 0d added
        # gmsh.model.mesh.addNodes(2, 1, self.nodes_inserted, self.coords)
        
        # for i in range(len(self.boundary_gmsh_identifier)):
        #     self.corner_nodes=self.boundary_gmsh_identifier[i].tolist()
        #     gmsh.model.mesh.addElementsByType(i + 1, 15, [], self.corner_nodes) 
        gmsh.model.mesh.addNodes(2, 1, self.nodes_inserted, self.coords)
        
        for extracted_boundary_name in  self.boundary_gmsh_identifier:

            self.bound=extracted_boundary_name.tolist()[0]
            gmsh.model.mesh.addElementsByType(self.boundary_nodes_ids[self.bound][0], 15, [], [self.boundary_nodes_ids[self.bound][0]])
            

        
       

    def __Floor1dElementsDefinition(self):
        self.total_line_element=[]       

        # 1d connectivities area extracted 
        for extracted_boundary_name in  self.boundary_gmsh_identifier:
            self.bound=extracted_boundary_name.tolist()[0]
            self.line_element=[]
            for i in range(len(self.boundary_nodes_ids[self.bound])-1):
                line=[self.boundary_nodes_ids[self.bound][i],self.boundary_nodes_ids[self.bound][i+1]]
                
                self.line_element.extend(line)
            self.total_line_element.append(self.line_element)
        
        # Elements 1d added into floor geometry
        for i in range(len(self.total_line_element)):    
            gmsh.model.mesh.addElementsByType(i+1, 1, [],self.total_line_element[i])

    def __Floor2dElementsDefinition(self):       
        ConnectivitiesTotal=[]
        # 2d connectivities area extracted 
        for element in self.elevated_mesh_model_part.Elements:
            geom=element.GetGeometry()
            for i in range(geom.PointsNumber()):
                node=geom[i]
                ConnectivitiesTotal.append(node.Id)
        gmsh.model.geo.removeAllDuplicates()
        # Elements 2d added into floor geometry
        gmsh.model.mesh.addElementsByType(1, 2, [], ConnectivitiesTotal)

    def __CreateFloorDiscreteGeometry(self):
        # Floor geometry is redefined 
        gmsh.model.mesh.reclassifyNodes()
        gmsh.model.mesh.createGeometry()

    def __CreateTopSurfaceModel(self):
        self.__TopSurfaceContourDefinition()
        self.__SavingTopMeshInformation()
        self.__AddingToNewGmshModelTopEntities()
        self.__TopSurfaceDiscretization()
        self.__BuiltBoundaryWalls()

    #TODO: This should be done using a generic function since the same procedure is done in other python module
    def __TopSurfaceContourDefinition(self):
        self.lines_ids_top=[]
        self.physical_group_name=[]
        self.total_elevation=self.maximum_terrain_elevation+self.elevation
        for bound in self.boundary_user_name:
            self.top_nodal_identifier=[]
            tolerance=1e-12
            for point in self.gmsh_geometry_dictionary[bound]:
                node=gmsh.model.geo.addPoint(point[0],point[1],self.total_elevation)
                self.top_nodal_identifier.append(node)
            line=gmsh.model.geo.addSpline(self.top_nodal_identifier)     
            self.lines_ids_top.append(line)
        gmsh.model.geo.removeAllDuplicates()
        top_surface_loop=gmsh.model.geo.addCurveLoop(self.lines_ids_top)
        self.top_surface_id=gmsh.model.geo.addPlaneSurface([top_surface_loop])
        gmsh.model.geo.synchronize()
        top_surface_boundary_id=gmsh.model.addPhysicalGroup(2,[self.top_surface_id])
        self.physical_group_name.append(top_surface_boundary_id)
        gmsh.model.setPhysicalName(2, top_surface_boundary_id, self.top_model_part_name)

        gmsh.model.geo.removeAllDuplicates()

        gmsh.model.geo.synchronize()

        NN = 10
        for c in gmsh.model.getEntities(1):
            gmsh.model.mesh.setTransfiniteCurve(c[1], NN)

        gmsh.model.mesh.generate(2)
    def __SavingTopMeshInformation(self):
        self.top_mesh_information = {}
        for top_entity in gmsh.model.getEntities():
            self.top_mesh_information[top_entity] = (gmsh.model.getBoundary([top_entity]),
                    gmsh.model.mesh.getNodes(top_entity[0], top_entity[1]),
                    gmsh.model.mesh.getElements(top_entity[0], top_entity[1]))
    def __AddingToNewGmshModelTopEntities(self):

        # 1) new model is created, gmsh model name is choosed randomly.
        gmsh.model.add('new_model')

        # 2) create discrete entities in the new model and copy top surface mesh
        for top_entity in sorted(self.top_mesh_information):
            gmsh.model.addDiscreteEntity(top_entity[0], top_entity[1], [b[1] for b in self.top_mesh_information[top_entity][0]])
            gmsh.model.mesh.addNodes(top_entity[0], top_entity[1], self.top_mesh_information[top_entity][1][0], self.top_mesh_information[top_entity][1][1])
            gmsh.model.mesh.addElements(top_entity[0], top_entity[1], self.top_mesh_information[top_entity][2][0], self.top_mesh_information[top_entity][2][1], self.top_mesh_information[top_entity][2][2])
        gmsh.model.mesh.createGeometry()

    def __TopSurfaceDiscretization(self):
        self.total_nodes_boundary_id_top=[]
        self.total_top_external_points=[]
        # Getting Nodes from contour Surface 
        for i in range(len(self.total_boundaries_names)):
            Entity_to_analyse= [(1,self.lines_ids_top[i])]
            NodesBoundaryId_Top=gmsh.model.mesh.getNodes(1,self.lines_ids_top[i],includeBoundary=True ) # obtenemos la lista de nodos paara cads entidad de linea =>> unicamnete considerando los internodos ( nada de los extremos)
            ExternalPoints_Top=gmsh.model.getBoundary(Entity_to_analyse,oriented = False) #  obtenemos los puntos extremos de la linea y ademas le marcamos que nos indique la dirección de la linea 
            InitialPoint_Top=ExternalPoints_Top[0]
            FinalPoint_Top=ExternalPoints_Top[1]

            InitialPointNode_Top=gmsh.model.mesh.getNodes(InitialPoint_Top[0],InitialPoint_Top[1])
            FinalPointNode_Top=gmsh.model.mesh.getNodes(FinalPoint_Top[0],FinalPoint_Top[1])
            Top_external_points=[ExternalPoints_Top[0][1],InitialPointNode_Top[0],ExternalPoints_Top[1][1],FinalPointNode_Top[0]]
            self.total_top_external_points.append(Top_external_points)
            self.total_nodes_boundary_id_top.append(NodesBoundaryId_Top[0])

        TotalNodesBoundaryId_floor=[]
        Total_Floor_new_external_points=[]
        for line in self.lines_discrete_entities:
            
            NodesBoundaryId_floor=gmsh.model.mesh.getNodes(1,line,includeBoundary=True)
            TotalNodesBoundaryId_floor.append(NodesBoundaryId_floor[0])
            ExternalPoints_Floor_new=gmsh.model.getBoundary([(1,line)],oriented = False) #  obtenemos los puntos extremos de la linea y ademas le marcamos que nos indique la dirección de la linea 
            InitialPoint_Floor_new=ExternalPoints_Floor_new[0]
            FinalPoint_Floor_new=ExternalPoints_Floor_new[1]
            InitialPointNode_Floor_new=gmsh.model.mesh.getNodes(InitialPoint_Floor_new[0],InitialPoint_Floor_new[1])
            FinalPointNode_Floor_new=gmsh.model.mesh.getNodes(FinalPoint_Floor_new[0],FinalPoint_Floor_new[1])
            Floor_new_external_points=[ExternalPoints_Floor_new[0][1],InitialPointNode_Floor_new[0],ExternalPoints_Floor_new[1][1],FinalPointNode_Floor_new[0]]
            Total_Floor_new_external_points.append(Floor_new_external_points)


        self.NewFloor_SurfaceDataBase=BoundaryNodalIdentification(self.total_boundaries_names,TotalNodesBoundaryId_floor,Total_Floor_new_external_points)
        self.BoundaryNodesIds_newfloor=self.NewFloor_SurfaceDataBase.NodesIdentitiesbyBoundary()
        self.TopSurfaceDataBase=BoundaryNodalIdentification(self.total_boundaries_names,self.total_nodes_boundary_id_top,self.total_top_external_points)

        self.BoundaryNodesIds_Top=self.TopSurfaceDataBase.NodesIdentitiesbyBoundary()
        BoundaryDictionary_Top=self.TopSurfaceDataBase.GetBoundaryNames()

    def __BuiltBoundaryWalls(self):
        self.ConectivitiesByBoundary=self.__AuxiliarySkinTriangulationGmsh(self.BoundaryNodesIds_Top,self.BoundaryNodesIds_newfloor,self.boundary_gmsh_identifier)
   
    def __AuxiliarySkinTriangulationGmsh(self,TopNodesbyBoundary,FloorNodesbyBoundary,total_boundaries_names): 
        connectivities_by_boundary={}
        for extracted_boundary_name in total_boundaries_names:
            bound=extracted_boundary_name.tolist()[0]
            connectivities=[]
            for j in range(len(TopNodesbyBoundary[bound])-1):
                # PRIMER TRIANGULO DEL SEGMENTO (se insertar todos en una unica lista para aña)
                connectivities.append(TopNodesbyBoundary[bound][j])
                connectivities.append(self.BoundaryNodesIds_newfloor[bound][j])
                connectivities.append(self.BoundaryNodesIds_newfloor[bound][j+1])

                #SEGUNDO TRIANGULO DEL SEGMENTO
                connectivities.append(TopNodesbyBoundary[bound][j])
                connectivities.append(self.BoundaryNodesIds_newfloor[bound][j+1])
                connectivities.append(TopNodesbyBoundary[bound][j+1])
            connectivities_by_boundary[bound]=connectivities
        return connectivities_by_boundary

    def __Gmsh3dDiscreteMesh(self):
        # ConectivitiesByBoundary=SkinTriangulationGmsh(BoundaryNodesIds_Top,BoundaryNodesIds_newfloor,self.total_boundaries_names)

        FloorPoints= self.NewFloor_SurfaceDataBase.ExternalPointEntity()
        TopPoints=self.TopSurfaceDataBase.ExternalPointEntity()

        # IdsLineDict={}
        control_check=[]
        InitialLines=[]
        for i in range(len( self.total_boundaries_names)):
            Bound=self.total_boundaries_names[i].tolist()[0]
    
            initialline=gmsh.model.addDiscreteEntity(1,-1,[FloorPoints[Bound][0],TopPoints[Bound][0]])
            gmsh.model.mesh.addElementsByType(initialline, 1, [],[self.BoundaryNodesIds_newfloor[Bound][0],self.BoundaryNodesIds_Top[Bound][0]])
            # finallines=gmsh.model.addDiscreteEntity(1,-1,[TopPoints[Bound][1],FloorPoints[Bound][1]])
            # gmsh.model.mesh.addElementsByType(finallines, 1, [],[BoundaryNodesIds_newfloor[Bound][-1],BoundaryNodesIds_Top[Bound][-1]])
            Idwithpoint=[initialline,FloorPoints[Bound][0]]
            InitialLines.append(initialline)
            control_check.append(Idwithpoint)

        endlines=[]
        for i in range (len(self.total_boundaries_names)):
            Bound=self.total_boundaries_names[i].tolist()[0]
            for element in control_check:
                if FloorPoints[Bound][1] == element[1]:
                    endlines.append(element[0])

        FloorPhysical=gmsh.model.addPhysicalGroup(2,[self.entity_floor])
        gmsh.model.setPhysicalName(2,FloorPhysical, self.floor_model_part)

        TopPhysical=gmsh.model.addPhysicalGroup(2,[self.top_surface_id])
        gmsh.model.setPhysicalName(2,TopPhysical,self.top_model_part_name)

        test=[]
        for i in range(len( self.total_boundaries_names)):
            Bound=self.total_boundaries_names[i].tolist()[0]
            initial=InitialLines[i]
            Topline=self.lines_ids_top[i]
            final=endlines[i]
            FloorLine= Bound
            SurfaceSkin=gmsh.model.addDiscreteEntity(2,-1,[initial,final,Topline,FloorLine])
            gmsh.model.mesh.addElementsByType(SurfaceSkin,2,[],self.ConectivitiesByBoundary[Bound])
            AssigningiBoundary=gmsh.model.addPhysicalGroup(2,[SurfaceSkin])
            gmsh.model.setPhysicalName(2,AssigningiBoundary,self.boundary_user_name[i])
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
        self.all_entities_surface=gmsh.model.getEntities(2)
        self.all_entities_volumes=gmsh.model.getEntities(3)  
        self.color_dictionary=self.__DictionaryForSubModelPart(self.all_entities_surface,self.all_entities_volumes)     
        gmsh.option.setNumber("Mesh.Algorithm3D",10)
        gmsh.option.setNumber("Mesh.MeshSizeMin",self.mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax",self.mesh_size)
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(3)
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()
    def GetKratosColorsIdentifiers(self):
        return self.color_dictionary

    def __ExportingMeshToMdpa(self):
        
        gmsh.write(self.file_name+"_3d.vtk")
        meshing=meshio.read(self.file_name+"_3d.vtk")
        meshio.mdpa.write(self.file_name+"_3d.mdpa", meshing)
        gmsh.clear()
        gmsh.finalize()
        toedit_mdpa=open(self.file_name+"_3d.mdpa","r")
        edited_mdpa = open("test.mdpa", 'w')
        checkWords = ("Begin Elements Triangle3D3","Begin Elements Tetrahedra3D4","Begin ElementalData CellEntityIds","End ElementalData CellEntityIds")
        repWords = ("Begin Elements Element3D3N","Begin Elements Element3D4N","Begin ElementalData ACTIVATION_LEVEL","End ElementalData")
        for line in toedit_mdpa:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            edited_mdpa.write(line)
        toedit_mdpa.close()
        edited_mdpa.close()
        if os.path.exists(self.file_name+"_3d.mdpa"):
            os.remove(self.file_name+"_3d.mdpa")
            os.rename("test.mdpa",self.file_name+"_3d.mdpa")

    def GetBoundaryNames(self):
        return self.boundary_type
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
        self.__ReadingKratosTerrainElevatedMeshGmsh()
        self.__FromMeshToDiscretizatedFloorModel()
        self.__CreateTopSurfaceModel()
        self.__Gmsh3dDiscreteMesh()
        self.__ExportingMeshToMdpa()

    def __DictionaryForSubModelPart(self,AllEntitiesSurface,AllentitiesVolumes):
        surface_boundary_identifiers=[]
        volume_boundary_identifiers=[]
        BoundarybyDimension={}
        for entity in AllEntitiesSurface:
            boundary_identifier=gmsh.model.getPhysicalGroupsForEntity(entity[0],entity[1])
            user_boundary_name=gmsh.model.getPhysicalName(entity[0],boundary_identifier[0])
            related_property=[boundary_identifier[0],user_boundary_name]
            surface_boundary_identifiers.append(related_property)
        BoundarybyDimension[2]=surface_boundary_identifiers
        for entity in AllentitiesVolumes:
            boundary_identifier=gmsh.model.getPhysicalGroupsForEntity(entity[0],entity[1])
            user_boundary_name=gmsh.model.getPhysicalName(entity[0],boundary_identifier[0])
            
            check=[boundary_identifier[0],user_boundary_name]
            volume_boundary_identifiers.append(check)
        BoundarybyDimension[3]=volume_boundary_identifiers
        return BoundarybyDimension
class BoundaryNodalIdentification():
    def __init__(self,BoundaryType,TotalNodeBoundaryId,ExternalPoint):
        self.boundary_type=BoundaryType
        self.total_node_boundary=TotalNodeBoundaryId
        self.external_point=ExternalPoint
    def NodesIdentitiesbyBoundary(self):
        NodesIdsbyBoundary={}
        for i in range(len(self.boundary_type)):
            bound=self.boundary_type[i].tolist()[0]
            NodesList=self.total_node_boundary[i].tolist()
            self.initial_point_Id=NodesList[len(NodesList)-2]
            self.final_point_Id=NodesList[-1]
            NodesList.remove(self.initial_point_Id)
            NodesList.insert(0,self.initial_point_Id)
            NodesIdsbyBoundary[bound]=NodesList
        return NodesIdsbyBoundary
    def ExternalPointEntity(self):
        TotalNodes=self.NodesIdentitiesbyBoundary()
        PointEntities={}
        for i in range(len(self.boundary_type)):
            bound=self.boundary_type[i].tolist()[0]
            InitialNode=TotalNodes[bound][0]
            FinalNode=TotalNodes[bound][-1]
            FirtsNode=self.external_point[i][1].tolist()[0]
    
            if FirtsNode== InitialNode:
                PointExt=[self.external_point[i][0],self.external_point[i][2]]
            else:
                PointExt=[self.external_point[i][2],self.external_point[i][0]]
            PointEntities[bound]= PointExt   
        
        return PointEntities
    
    def GetBoundaryNames(self):
        return self.boundary_type
                