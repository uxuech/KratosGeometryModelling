import shapefile
import gmsh
import sys
import meshio
import os
# From external file the geometry is read. The code is prepared for .shp files.  TODO:  implementation for other files types.
class BuildingMeshTool:

    def __init__(self, settings):
        self._file_name = settings["building_file_name"].GetString()
        gmsh.initialize(sys.argv)
        gmsh.model.add("BuildingMesh")
        self.mesh_size = settings["mesh_size"].GetDouble()
        self.gmsh_format = ".vtk"


    def Execute(self):
        self.attributes=self.SavingShapefileAttributes()
        self.coordinates = self.SavingShapefileCoordinates()
        self.building_dic_information = self.CreateBuildingDictionary()
        self.CreateBuildingSurfaceGeometry()
        self.__Gmsh3dMesh()
        self.__ExportingMeshToMdpa()
    def SavingShapefileAttributes(self):
        sf = shapefile.Reader(self._file_name)
        extracted_atributes = sf.shapeRecords()
        return extracted_atributes

    def SavingShapefileCoordinates(self):
        sf = shapefile.Reader(self._file_name)
        extracted_coordinates = sf.shapes()
        return extracted_coordinates


    def CreateBuildingDictionary(self):
        bulding_dic = {}
        self.building_id_list=[]
        for i in range(len(self.coordinates)):
            Building_id = self.attributes[i].record[0]
            Bulding_elevation = self.attributes[i].record[1]
            Coordinates_building_floor = self.coordinates[i].points
            bulding_dic[Building_id] = [Coordinates_building_floor, Bulding_elevation]
            self.building_id_list.append(Building_id)
        return bulding_dic

    def CreateBuildingSurfaceGeometry(self):
        for building in self.building_id_list:
            nodesId=[]
            linesIdsFloor=[]
            self.polyline_list=self.building_dic_information[building][0]
            self.polyline_list.pop()
            print(self.polyline_list)
            self.height_extrusion = self.building_dic_information[building][1]
            for point in self.polyline_list:
                node=gmsh.model.geo.addPoint(point[0],point[1],self.height_extrusion,self.mesh_size)
                nodesId.append(node)
            for i in range(len(nodesId)-1):
                line = gmsh.model.geo.addLine(nodesId[i], nodesId[i+1])
                linesIdsFloor.append(line)
            line = gmsh.model.geo.addLine(nodesId[-1], nodesId[0])
            linesIdsFloor.append(line)
            gmsh.model.geo.removeAllDuplicates()
            building_contour = gmsh.model.geo.addCurveLoop(linesIdsFloor)
            gmsh.model.geo.synchronize()
            building_floor = gmsh.model.geo.addPlaneSurface([building_contour])
            self.tolerance_height = -1.2*self.height_extrusion
            gmsh.model.geo.extrude([(2, building_floor)], 0.0, 0.0,self.tolerance_height)
            gmsh.model.geo.synchronize()


    def __Gmsh3dMesh(self):
        # TODO: THIS FUNCTION SHOULD BE GENERAL FOR 2D 3D AND A NEW SIZE SHOULD BE ASKED HOW CAN WE RELEATE??

        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.MeshSizeMin", self.mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", self.mesh_size)
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(3)
        self.outputname = self._file_name+"_3d"+self.gmsh_format
        gmsh.write(self.outputname)


    def __ExportingMeshToMdpa(self):

        gmsh.write(self._file_name+"_3d.vtk")
        meshing = meshio.read(self._file_name+"_3d.vtk")
        meshio.mdpa.write(self._file_name+"_3d.mdpa", meshing)
        gmsh.clear()
        gmsh.finalize()
        toedit_mdpa = open(self._file_name+"_3d.mdpa", "r")
        edited_mdpa = open("test.mdpa", 'w')
        checkWords = ("Begin Elements Triangle3D3", "Begin Elements Tetrahedra3D4",
                      "Begin ElementalData CellEntityIds", "End ElementalData CellEntityIds")
        repWords = ("Begin Elements Element3D3N", "Begin Elements Element3D4N",
                    "Begin ElementalData ACTIVATION_LEVEL", "End ElementalData")
        for line in toedit_mdpa:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            edited_mdpa.write(line)
        toedit_mdpa.close()
        edited_mdpa.close()
        if os.path.exists(self._file_name+"_3d.mdpa"):
            os.remove(self._file_name+"_3d.mdpa")
            os.rename("test.mdpa", self._file_name+"_3d.mdpa")





