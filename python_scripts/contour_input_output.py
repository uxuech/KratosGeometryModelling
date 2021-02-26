class ContourInputOutput:

    def __init__(self, file_name, file_format=".shp", round_coords=True, move_to_origin=True):
        print("constructor")
        self._file_name = file_name
        self._file_format = file_format
        self._round_coords = round_coords
        self._move_to_origin = move_to_origin

    def Execute(self):
        self.__ReadFile
        if self._round_coords:
            __RoundCoords()
        if self._move_to_origin:
            __MoveToOrigin()
        self.__SetBoundariesInformation()
        self.__CollapseEndPoints()
        self.__ReorderBoundaries()
        self.__MergeInnerPoints()
        self.__SetCountourData()

    def __ReadFile(self):

    def __RoundCoords(self):

    def __MoveToOrigin(self):

    def __SetBoundariesInformation(self):

    def __CollapseEndPoints(self):

    def __ReorderBoundaries(self):

    def __MergeInnerPoints(self):

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
