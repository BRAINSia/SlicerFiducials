# -*- coding: utf-8 -*-
# File: SlicerFiducials.py
# Author: Arjit Jain <thearjitjain@gmail.com>
# Modified by: Alexander Powers <powersa15@gmail.com>
from copy import deepcopy

import itk
import numpy as np
import pandas as pd

from .enums import Format, Space

HEADER = {}
HEADER[
    Format.ORIGINAL_MARKUP
] = "# Markups fiducial file version = 4.10\n# CoordinateSystem = 0\n# columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n"
HEADER[Format.ORIGINAL] = "#label,x,y,z,sel,vis\n"


class SlicerFiducials(object):
    def __init__(
        self,
        fcsv_filename: str = None,
        df: pd.DataFrame = None,
        image_filename: str = None,
        convertRAStoLPS: bool = True,
    ):
        """
        constructor for this class. this class can be initialized by either the name(path) of the fcsv file or by
        a pandas dataframe object. fcsv file is read only when no dataframe has been passed.
        :param fcsv_filename: path of the fcsv file
        :param df: pandas dataframe object
        :param image_filename: path to the image
        :param convertRAStoLPS: whether to convert Right-Anterior-Superior to Left-Posterior-Superior
        """

        # load all params passed in
        self.fcsv_filename = fcsv_filename
        self.image_filename = image_filename
        self.df = df
        self.convertRAStoLPS = convertRAStoLPS

        if self.fcsv_filename is None and self.df is None:
            raise ValueError("Either fcsv_filename or df must be defined.")

        self.image = None
        if self.image_filename is not None:
            self.image = itk.imread(self.image_filename)

        if self.df is None:
            self.df = pd.read_csv(self.fcsv_filename, comment="#", header=None)

        # create parameters to be initialized
        self.length = None
        self.fiducialToPhysical = {}
        self.format = None
        self.indices = None

        # initialize parms
        self.set_params()

    def set_params(self):
        """
        :return:
        """
        self.length = self.df.shape[0]
        if self.df.shape[1] == 6:
            self.format = Format.ORIGINAL
            self.df.columns = ["label", "x", "y", "z", "sel", "vis"]

        elif self.df.shape[1] == 14:
            self.format = Format.ORIGINAL_MARKUP
            self.df.columns = [
                "id",
                "x",
                "y",
                "z",
                "ow",
                "ox",
                "oy",
                "oz",
                "vis",
                "sel",
                "lock",
                "label",
                "desc",
                "associatedNodeID",
            ]
        else:
            raise ValueError("Please check your input FCSV file")
        self.df.index = self.df["label"]
        self.indices = list(self.df["label"])
        self.indices.sort()
        self.df = self.df.reindex(labels=self.indices)
        # create fiducialToPhysical dictionary { fiducial_name --> [x,y,z] }
        self.create_dict()

    def create_dict(self):
        """
        :return:
        """
        labels = self.df["label"]
        x = np.array(self.df["x"]).reshape(-1, 1)
        y = np.array(self.df["y"]).reshape(-1, 1)
        z = np.array(self.df["z"]).reshape(-1, 1)
        if self.convertRAStoLPS:
            x = -1 * x
            y = -1 * y
        vector = np.concatenate((x, y, z), axis=1)
        self.fiducialToPhysical = dict(zip(labels, vector))

    def euclidean_distance(self, fid1: str, fid2: str) -> float:
        """
        :param fid1: label of fiducial 1
        :param fid2: label of fiducial 2
        :return: the euclidean distance between fid1 and fid2 in the pixel space
        """
        return np.linalg.norm(
            self.fiducialToPhysical[fid1] - self.fiducialToPhysical[fid2]
        )

    def __str__(self):
        return str(self.fiducialToPhysical)

    def __iter__(self):
        """
        :return: an iterable of the form label, point where label is a string and point is the 3D location
        """
        return iter(self.fiducialToPhysical.items())

    @staticmethod
    def diff_files(file1, file2):
        """
        :param file1: SlicerFiducials
        :param file2: SlicerFiducials
        :return: SlicerFiducials object calculating the difference between corresponding fiducials of file1 and file2
        """
        if file1.names() != file2.names():
            raise ValueError
        df = file1.df.copy()
        df2 = file2.df.copy()
        df["x"] = df["x"] - df2["x"]
        df["y"] = df["y"] - df2["y"]
        df["z"] = df["z"] - df2["z"]
        return SlicerFiducials(df=df)

    def names(self):
        """
        :return: list of labels of all the fiducials in the object
        """
        return list(self.df["label"])

    def get_format(self, format: Format) -> pd.DataFrame:
        """
        :param format: desired format
        :return: dataframe in the desired format
        """
        dfToReturn = None
        if format == Format.ORIGINAL:
            dfToReturn = pd.DataFrame(self.df[["label", "x", "y", "z", "sel", "vis"]])
        elif format == Format.ORIGINAL_MARKUP:
            ow_ox_oy = pd.DataFrame(
                np.zeros((self.length, 3), dtype=float), columns=["ow", "ox", "oy"]
            )
            ow_ox_oy.index = self.df.index
            lock = pd.DataFrame(np.zeros((self.length, 1)), columns=["lock"])
            lock.index = self.df.index
            oz = pd.DataFrame(np.ones((self.length, 1), dtype=float), columns=["oz"])
            oz.index = self.df.index
            id = pd.DataFrame(
                ["vtkMRMLMarkupsFiducialNode_" + str(i) for i in np.arange(self.length)]
            )
            id.index = self.df.index
            temp_df = pd.concat(
                (
                    id,
                    self.df[["x", "y", "z"]],
                    ow_ox_oy,
                    oz,
                    self.df[["vis", "sel"]],
                    lock,
                    self.df["label"],
                ),
                ignore_index=False,
                axis=1,
            ).round(3)
            temp_df = temp_df.reindex(
                columns=temp_df.columns.tolist() + ["desc", "associatedNodeID"]
            )
            temp_df.columns = [
                "id",
                "x",
                "y",
                "z",
                "ow",
                "ox",
                "oy",
                "oz",
                "vis",
                "sel",
                "lock",
                "label",
                "desc",
                "associatedNodeID",
            ]
            dfToReturn = pd.DataFrame(temp_df)
        else:
            raise NotImplementedError
        dfToReturn.index = dfToReturn["label"]
        return dfToReturn.reindex(labels=self.indices)

    def query(self, name: str, space: Space = Space.PHYSICAL) -> np.ndarray:
        """
        query for single landmark point using label. by default in physical space
        :param name: label of the landmark point
        :param space: 'physical' or 'index'.
        :return:
        """
        physical = self.fiducialToPhysical[name]
        if space == Space.INDEX:
            assert self.image is not None
            return np.array(
                self.image.TransformPhysicalPointToContinuousIndex(physical)
            )
        return physical

    def set(self, name: str, xyz_array: np.ndarray) -> None:
        """
        set [x,y,z] for a landmark by name. by default in physical space
        :param name: label of the landmark point
        :param xyz_array: physical space location of the landmark
        :return:
        """
        try:
            assert len(xyz_array) == 3
        except AssertionError as _:
            raise Exception("Array length must be 3.")

        self.fiducialToPhysical[name] = xyz_array

        if self.convertRAStoLPS:
            xyz_array[0] = -1 * xyz_array[0]
            xyz_array[1] = -1 * xyz_array[1]

        self.df.loc[self.df["label"] == name, "x"] = xyz_array[0]
        self.df.loc[self.df["label"] == name, "y"] = xyz_array[1]
        self.df.loc[self.df["label"] == name, "z"] = xyz_array[2]

    def apply_sitk_transform(self, sitk_transform, inplace=True):
        """
        applies a simpleitk transform to all of the points in the SlicerFiducials object
        :param sitk_transform: A SimpleITK transform to apply to all of the points in the fcsv
        :param xyz_array: optional param to do transform inplace or return a new SlicerFiducials object
        :return: may return a SlicerFiducials object depending on if it is done inplace
        """
        try:
            assert hasattr(sitk_transform, "TransformPoint")
        except AssertionError as e:
            raise TypeError("sitk_transform must implement the TransformPoint method.")
        if inplace:
            for name in self.names():
                point = self.query(name)
                transformed_point = sitk_transform.TransformPoint(point)
                self.set(name, np.array(transformed_point))
        else:
            fiducials_to_return = deepcopy(self)
            for name in fiducials_to_return.names():
                point = fiducials_to_return.query(name)
                transformed_point = sitk_transform.TransformPoint(point)
                fiducials_to_return.set(name, np.array(transformed_point))
            return fiducials_to_return

    def write(self, name: str, format: Format = None) -> None:
        """
        Writes data to file in the desired format
        :param name: path to save
        :param format: format to save in
        :return:
        """
        if not format:
            format = self.format
        format_df = self.get_format(format)
        with open(name, "w") as file:
            file.write(HEADER[format])
            format_df.to_csv(file, index=False, header=False, float_format="%.3f")
