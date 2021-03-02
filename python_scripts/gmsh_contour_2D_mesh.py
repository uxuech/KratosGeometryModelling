gmsh.model.add("Volumemesh")
linesIdsFloor=[]
supernodeIds=[]
# --- Meshing study area according to input user colors
physicalgroupname=[]
nodesIds6=[]
            nodesIds=[]
            tolerance=1e-12
            supernodeId=[]
            BeginNodeId=[]
            EndNodeId=[]
            newlines=MergeRepeatedPoint(merged_polylines_dict[bound],tolerance)
class GmshContour2dMeshGenerator():
    def __init__(self, BoundaryNames,Polylines,mesh_size="5",outputfilename):
        print("constructor")
        self._boundary_name = BoundaryName
        self.contour_polylines = Polylines
        self.mesh_size=mesh_size
        self.outputfilename=outputfilename

    def GmshGeometryGeneration(self):
        nodesIds=[]
        linesIdsFloor=[]
        for bound in self._boundary_name:
            for point in self.contour_polylines:
                node=gmsh.model.geo.addPoint(point[0],point[1],0,self.mesh_size)
                nodesIds.append(node)
            line=gmsh.model.geo.addSpline(nodesIds)
            # TODO: DO WE REALLY THIS BEGIN POINTS???
            # BeginNodeId.append(nodesIds[0])
            # EndNodeId.append(nodesIds[-1])
            linesIdsFloor.append(line)
            gmsh.model.geo.synchronize()
            lineId=gmsh.model.addPhysicalGroup(1,[line])
           
            gmsh.model.setPhysicalName(2, lineId, bound)
            physicalgroupname.append(lineId)
        gmsh.model.geo.removeAllDuplicates()
        # TODO: AUTOMATIZE ACCORDING TO USER BOUNDARY FLOOR--DO WE REALLY HE IS NO GOING TO GIVE THAT??
        gmsh.model.geo.addCurveLoop(linesIdsFloor)
        gmsh.model.geo.synchronize()
        floor=gmsh.model.geo.addPlaneSurface([1])
        gmsh.model.geo.synchronize()
        g=gmsh.model.addPhysicalGroup(2,[floor])
        physicalgroupname.append(g)
        gmsh.model.setPhysicalName(2, g, "floorsurf")       

    def Gmsh2dMesh(self):
        # TODO: THIS FUNCTION SHOULD BE GENERAL FOR 2D 3D AND A NEW SIZE SHOULD BE ASKED HOW CAN WE RELEATE??
        gmsh.option.setNumber('Mesh.MeshSizeMin',15)
        gmsh.option.setNumber('Mesh.MeshSizeMax', 15)
        gmsh.model.mesh.generate(2)
    def GmshMdpaToKratos(self):
        # TODO: with different files typs vtk mdpa
        gmsh.write(self.outputfilename)
        meshing=meshio.read(self.outputfilename)
        meshio.mdpa.write(self.outputfilename, meshing)", meshing)
        # TODO: this should be automatized__always like that ??ñe
        toedit_mdpa=open("test.mdpa","r")
        edited_mdpa = open("test_good.mdpa", 'w')
        checkWords = ("Begin Elements Line2D2","Begin Elements Triangle2D3","Begin ElementalData CellEntityIds","End ElementalData CellEntityIds")
        repWords = ("Begin Elements Element2D2N","Begin Elements Element2D3N","Begin ElementalData ACTIVATION_LEVEL","End ElementalData")
        for line in toedit_mdpa:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            edited_mdpa.write(line)
        toedit_mdpa.close()
        edited_mdpa.close()
