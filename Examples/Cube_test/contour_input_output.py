import shapefile    
import gmsh
import sys
import meshio
class ContourInputOutput:

    def __init__(self, settings):
       self._file_name = settings["file_name"].GetString()
       self._round_coords=settings["round_coordinates"].GetBool()
       self._move_to_origin=settings["move_to_origen"].GetBool()
       self._file_format=settings["file_format"].GetString()
       self._tolerance_repeated_points=settings["tolerance_repeated_points"].GetDouble()
       
    
    
    
    def Execute(self):

        self.__ReadFile()
        if self._round_coords:
            self.__RoundCoords()
        else:
            warning_msg="WARNING: Contour could not be completly closed.Please be sure that the polygone is closed"
            print(warning_msg)
        if self._move_to_origin:
            self.__ContourBoundingBox()
            self.__MoveToOrigin()
        self.__AssigningAttributeToPolyline()
        self.__ContourBoundaryName()
        self.__IdentifyRepeteadedPoints()
        self.__OrderPointsandPolylinesByAttibute()
        self.__PolylinesRepeatedPoint()
        self.__GetPolylinesGmshContourDic()


    def __ReadFile(self):
        # From external file the geometry is read. The code is prepared for .shp files.  TODO:  implementation for other files types. 
        sf = shapefile.Reader(self._file_name)
        self.extracted_atributes = sf.shapeRecords()
        self.extracted_coordinates= sf.shapes()
        print("Shapefile is read")


    def __RoundCoords(self):
        # Coordinates of study contour area are rounded in order to avoid issues with unclosed polygones.
        self.contour_shape_points_rounded=[]
        for i in range(len(self.extracted_coordinates)):
            self.total_coordinates=self.extracted_coordinates[i].points
            self.rounded_coordinates=[]
            for coordinates in self.total_coordinates:
                rounded_coordinates_point=[]
                for each_component in coordinates:
                    each_component=round(each_component,3)
                    rounded_coordinates_point.append(each_component)
                self.rounded_coordinates.append(rounded_coordinates_point)
            self.contour_shape_points_rounded.append(self.rounded_coordinates)
        print("Rounded Cordinate processes done") 


    def __ContourBoundingBox(self):
        # Getting the Contour bounding box in order to translate to an easier coordinates. Maybe this function can be useful for other propose from an external code. 
        x_cordinates=[]
        y_cordinates=[]
        for polyline in self.contour_shape_points_rounded:
            for polyline_points in polyline:
                x_cordinates.append(polyline_points[0])
                y_cordinates.append(polyline_points[1])

        self.max_value_x=max(x_cordinates)
        self.min_value_x=min(x_cordinates)
        self.max_value_y=max(y_cordinates)
        self.min_value_y=min(y_cordinates)
        self.contour_bounding_box=[[self.max_value_x,self.max_value_y],[self.min_value_x,self.min_value_y]]
        print("Contour Bonding Box done") 
        return self.contour_bounding_box

    def __MoveToOrigin(self):
        # The original coordinates are transformed to origin (0,0) in order to avoid issues. TODO: After all meshing process it should be implemented the option to remove coordinates(original coordinates )
        self.moved_total_coordinates=[]
        for polyline in self.contour_shape_points_rounded:
            polyline_with_coordinates_moved=[]

            for polyline_points in polyline:
                x=polyline_points[0]- self.min_value_x
                y=polyline_points[1]- self.min_value_y
                polyline_with_coordinates_moved.append([x,y])

            self.moved_total_coordinates.append(polyline_with_coordinates_moved)
        print("Coordinates Moved to origin ") 


    def __AssigningAttributeToPolyline (self):
        self.contour_polylines_and_attributes=[]
        self.complete_extracted_atributes_list=[]
        for i in range(len(self.extracted_atributes)):
            self.complete_extracted_atributes=self.extracted_atributes.record[0]
            self.contour_polylines_and_attributes.append([CompleteExtractedAtributes, RoundedTotalCoordinates[i]])
            self.complete_extracted_atributes_list.append(self.complete_extracted_atributes)
        print("Assigning Attribute To Polyline done")
    def __ContourBoundaryName(self):
        self.contour_boundary_name=[]
        self.complete_extracted_atributes_list.sort()
        for polyline_attribute in self.complete_extracted_atributes_list: 
            if polyline_attribute not in self.contour_boundary_name: 
                self.contour_boundary_name.append(polyline_attribute) 
        return self.contour_boundary_name
        print("Contour boundary name done ")

#TODO: DO WE REALLY NEED THIS FUNCTION IN CLEAN CODE
    def CreateBoundariesTypeDictionary(AllPolylinesDatabase, BoundaryTypesList):
        boundary_type_dict = {}
        for boundary_type in BoundaryTypesList:
            boundary_type_polys = []
            for polyline in AllPolylinesDatabase:
                if polyline.GetColor() == boundary_type:
                    boundary_type_polys.append(polyline)
            boundary_type_dict[boundary_type] = boundary_type_polys
        print( CreateBoundaries)
        return boundary_type_dict    
    
    def __IdentifyRepeteadedPoints(self):
        # Agrupate polilynes by boundary name and in and alphabetic order
        check_in_colors_list=self.contour_boundary_name
        self.repeated_points_in_geometry= []
        # TODO: DO WE REALLY NEED TO DO THIS?
        self.polylines_ordered_according_attribute = sorted(self.contour_polylines_and_attributes, key=lambda x: x[0])
        self.geometry_data_base=[]
        for polyline in self.polylines_ordered_according_attribute :
            new_polyline_data = PolylineData(polyline[0], polyline[1])
            self.geometry_data_base.append(new_polyline_data)
        self.polylines_data_base=CreateBoundariesTypeDictionary(self.geometry_data_base,self.contour_boundary_name)
        # Check if the current poliline endpoints are repeated in other polylines with the diiferent attribute.
        for polyline in self.geometry_data_base:
            polyline_attribute = polyline.GetColor()
            is_begin_repeated = CheckPointInAttributes(polyline_data.GetBeginPoint(), polyline_attribute, self.geometry_data_base, check_in_colors_list)
            is_end_repeated = CheckPointInAttributes(polyline_data.GetEndPoint(), polyline_attribute,self.geometry_data_base,check_in_colors_list)
            if len(is_begin_repeated) > 0:
                self.self.repeated_points_in_geometry(is_begin_repeated)
            if len(is_end_repeated) > 0:
                self.self.repeated_points_in_geometry(is_end_repeated)
            check_in_colors_list.pop(0)

    
    # def __MergeInnerPointsOfAttribute(self):
    def __OrderPointsandPolylinesByAttibute(self):
        orderedPolyline=[]
        i=1
        tol=1.0e-12
        merged_polylines_dict = {}
        for boundary_type in self.contour_boundary_name:
            self.merged_polylines_dict[boundary_type] = []
            for point in  self.self.repeated_points_in_geometry: 
                right_side_color=point.GetColorOne()
                # Getting all polylines with Right_side_color
                right_side_polylines = self.polylines_data_base[right_side_color]
                # Getting all polylines with left_side_color
                left_side_color=point.GetColorTwo()
                left_side_polylines = self.polylines_data_base[left_side_color]
                repeated_point_coord = point.GetCoordinates() 
                #TODO: PONERLO COMO RUBEN EN UNA LINEA LAS DOS OPCIONES CHECKEARLO
                if right_side_color == boundary_type:
                   same_att_polylines=right_side_polylines
                elif left_side_color== boundary_type:
                    same_att_polyline=left_side_polylines
                for polyline in same_att_polylines:
                    if repeated_point_coord == polyline.GetBeginPoint():
                        # Append 1st polyline from the color origin
                        for point in polyline.GetAllPoints():
                            self.merged_polylines_dict[boundary_type].append(point)
                        # From the 1st polyline end append the next one
                        first_polyline = polyline
                        aux_polyline_list = same_att_polylines
                        aux_polyline_list.remove(first_polyline)
                        for i in range(len(aux_polyline_list)):
                            for aux_polyline in aux_polyline_list:
                                # Check the concatenation of polylines
                                if first_polyline.GetEndPoint() == aux_polyline.GetBeginPoint():
                                    # Append the polyline colors to the list
                                    for point in aux_polyline.GetAllPoints():
                                        merged_polylines_dict[boundary_type].append(point)
                                    # Update the current polyline
                                    first_polyline = aux_polyline
                                    aux_polyline_list.remove(first_polyline)
                                    break
                    elif repeated_point_coord == polyline.GetEndPoint():
                        # Append 1st polyline from the color origin
                        for point in polyline.GetAllPoints():
                            merged_polylines_dict[boundary_type].append(point)
                        # From the 1st polyline end append the next one
                        first_polyline = polyline
                        aux_polyline_list = a_polylines
                        aux_polyline_list.remove(first_polyline)
                        for i in range(len(aux_polyline_list)):
                            for aux_polyline in aux_polyline_list:
                                # Check the concatenation of polylines
                                if first_polyline.GetBeginPoint() == aux_polyline.GetEndPoint():
                                    # Append the polyline colors to the list
                                    for point in (aux_polyline.GetAllPoints()).reverse():
                                        merged_polylines_dict[boundary_type].append(point)
                                    # Update the current polyline
                                    first_polyline = aux_polyline
                                    aux_polyline_list.remove(first_polyline)
                                break
                    
    def PolylinesRepeatedPoint(Polylines,tolerance): 
        Bound=self.__ContourBoundaryName()
        self.polyline_gmsh_format=MergeRepeatedPoint(self.merged_polylines_dict[bound],tolerance)

    def GetPolylinesGmshContourDic(self):
        return self.self.polyline_gmsh_format

    # def __SetBoundariesInformation(self):
        
    #     self.polylines_ordered_according_attribute = sorted(self.contour_polylines_and_attributes, key=lambda x: x[0])
    #     polyline_data_base = []
    #     for polyline in all_polylines:
    #         new_polyline_data = PolylineData(polyline[0], polyline[1])
    #         # new_polyline_data = PolylineData(polyline[0], polyline[1][0], polyline[1][-1], polyline[1])
    #         polyline_data_base.append(new_polyline_data)
    #     polylines_dict = CreateBoundariesTypeDictionary(polyline_data_base, Boundariestype)
    #     att_end_pts = {}

    #     self.att_repeated = []
    #     check_in_colors_list = AtributesGroup

    #     for polyline_data in polyline_data_base:
    #         # Check if the current poliline endpoints are repeated in other polylines
    #         polyline_type = polyline_data.GetColor()
    #         is_begin_repeated = CheckPointInAttributes(polyline_data.GetBeginPoint(), polyline_type, polyline_data_base, check_in_colors_list)
    #         is_end_repeated = CheckPointInAttributes(polyline_data.GetEndPoint(), polyline_type, polyline_data_base, check_in_colors_list)

    #         if len(is_begin_repeated) > 0:
    #             self.att_repeated.extend(is_begin_repeated)
    #         if len(is_end_repeated) > 0:
    #             self.att_repeated.extend(is_end_repeated)
    #         check_in_colors_list.pop(0)

    def MergeRepeatedPoint(AttributePolylines, tolerance):
        NewAttributePolylines=[]
        for point  in AttributePolylines:
            if point not in NewAttributePolylines:
                NewAttributePolylines.append(point)

        AttributePolylines=NewAttributePolylines
        return AttributePolylines




    # def __CollapseEndPoints(self):

    # def __ReorderBoundaries(self):

    # def __MergeInnerPoints(self):

    def __SetCountourData(self):
        if not hasattr(self, "_countour_data"):
            #HACER COSAS
            self._countour_data = []
        else:
            err_msg = "Countour data has been created already."
            raise Exception(err_msg)

    def GetAllCountourData(self):
        return self._countour_data

    def GetCountourData(self, boundary_name):
        return self._countour_data[boundary_name]


# A class with the intersected point coordinates between two atrributes is created 

class PolylineRepeatedPoint():
    def __init__(self, ColorOne, ColorTwo, Coordinates):
        self.color_one = ColorOne
        self.color_two = ColorTwo
        self.coordinates = Coordinates

    def GetColorOne(self):
        return self.color_one

    def GetColorTwo(self):
        return self.color_two

    def GetCoordinates(self):
        return self.coordinates

# A Data base class is defined in order to characterized imported geometry(shapefile)

class PolylineData():
    def __init__(self, Color, AllPoints):
    # def __init__(self, Color, BeginPoint, EndPoint, AllPoints):
        self.color = Color
        #self.begin_point = BeginPoint
        #self.end_point = EndPoint
        self.all_points= AllPoints

    def GetColor(self):
        return self.color
    
    def GetBeginPoint(self):
        #return self.begin_point
        return self.all_points[0]

    def GetEndPoint(self):
        #return self.end_point
        return self.all_points[-1]

    def GetAllPoints(self):
        return self.all_points



