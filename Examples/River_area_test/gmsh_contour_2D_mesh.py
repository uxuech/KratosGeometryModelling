import shapefile    
import gmsh
import sys
import meshio

linesIdsFloor=[]
supernodeIds=[]
# --- Meshing study area according to input user colors
physicalgroupname=[]
nodesIds6=[]
class GmshContour2dMeshGenerator():
    def __init__(self,settings,BoundaryNames,Polylines):
        print("constructor")
        self._boundary_name = BoundaryNames
        self.contour_polylines = Polylines
        self.mesh_size=settings["mesh_size"].GetDouble()
        self.outputfilename=settings["output_file_name"].GetString()
        self.outputfilenamemdpa=settings["output_file_mdpa"].GetString()
        self.kratos_contour_mdpa=settings["kratos_file_name3"].GetString()
        gmsh.initialize(sys.argv)
        gmsh.model.add("Volumemesh")
        

    def __GmshGeometryGeneration(self):
        
        
        
        linesIdsFloor=[]
        for bound in self._boundary_name:
            nodesIds=[]
            print(bound)
            print(self.contour_polylines[bound])
            for point in self.contour_polylines[bound]:
                print(point)
                node=gmsh.model.geo.addPoint(point[0],point[1],0,self.mesh_size)
                nodesIds.append(node)
            line=gmsh.model.geo.addSpline(nodesIds)
            linesIdsFloor.append(line)
            gmsh.model.geo.synchronize()
            lineId=gmsh.model.addPhysicalGroup(1,[line])           
            gmsh.model.setPhysicalName(2, lineId, bound)
            physicalgroupname.append(lineId)

        gmsh.model.geo.removeAllDuplicates()
        gmsh.model.geo.addCurveLoop(linesIdsFloor)
        gmsh.model.geo.synchronize()
        floor=gmsh.model.geo.addPlaneSurface([1])
        gmsh.model.geo.synchronize()
        g=gmsh.model.addPhysicalGroup(2,[floor])
        physicalgroupname.append(g)
        gmsh.model.setPhysicalName(2, g, "floorsurf")       

    def __Gmsh2dMesh(self):
        # TODO: THIS FUNCTION SHOULD BE GENERAL FOR 2D 3D AND A NEW SIZE SHOULD BE ASKED HOW CAN WE RELEATE??
        gmsh.option.setNumber('Mesh.MeshSizeMin',15)
        gmsh.option.setNumber('Mesh.MeshSizeMax', 15)
        gmsh.model.mesh.generate(2)
        gmsh.write(self.outputfilename)
    def __MeshDiscretizationIdentification(self):

        self.total_boundaries_name=[]   
        self.total_nodes_boundary_id=[]
        self.total_external_points=[]
        for e in gmsh.model.getEntities():

            if e[0]==1:
                print("entra")
                print(e)
                NodesBoundaryId=gmsh.model.mesh.getNodes(e[0], e[1],includeBoundary=True)
                print("hola")
                print(NodesBoundaryId)
                ExternalPoints=gmsh.model.getBoundary([e],oriented = False)
                InitialPoint=ExternalPoints[0]
                FinalPoint=ExternalPoints[1]
                InitialPointNode=gmsh.model.mesh.getNodes(InitialPoint[0],InitialPoint[1])
                FinalPointNode=gmsh.model.mesh.getNodes(FinalPoint[0],FinalPoint[1])
                External_Point=[ExternalPoints[0][1],InitialPointNode[0],ExternalPoints[1][1],FinalPointNode[0]]
                self.total_external_points.append(External_Point)
                BoundaryName=gmsh.model.getPhysicalGroupsForEntity(e[0],e[1])
                print("hola")
                print(self.total_nodes_boundary_id)
                self.total_nodes_boundary_id.append(NodesBoundaryId[0])
                self.total_boundaries_name.append(BoundaryName)

    def GetTotalBoundariesName(self):
        return self.total_boundaries_name
    def GetTotalNodesBoundaryId(self):
        return self.total_nodes_boundary_id
    def GetTotalExternalPoints(self):
        return self.total_external_points


    def __GmshMdpaToKratos(self):
        # TODO: with different files typs vtk mdpa
        meshing=meshio.read(self.outputfilename)
        meshio.mdpa.write(self.outputfilenamemdpa, meshing)
        # TODO: this should be automatized__always like that ??ñe
        toedit_mdpa=open(self.outputfilenamemdpa,"r")
        edited_mdpa = open(self.kratos_contour_mdpa, 'w')
        checkWords = ("Begin Elements Line2D2","Begin Elements Triangle2D3","Begin ElementalData CellEntityIds","End ElementalData CellEntityIds")
        repWords = ("Begin Elements Element2D2N","Begin Elements Element2D3N","Begin ElementalData ACTIVATION_LEVEL","End ElementalData")
        for line in toedit_mdpa:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            edited_mdpa.write(line)
        toedit_mdpa.close()
        edited_mdpa.close()
    def Execute(self):
        self.__GmshGeometryGeneration()
        self.__Gmsh2dMesh()
        self.__MeshDiscretizationIdentification()
        
        self.__GmshMdpaToKratos()


