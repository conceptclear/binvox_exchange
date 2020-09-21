#!/usr/bin/python

"""script used to change binvox file into step file"""

import binvox_rw
import numpy as np

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound, TopoDS_Builder

from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone


def binvox_to_step(binvox_file, voxel_length, voxel_width, voxel_height, application_protocol="AP203"):
    """function used to change binvox file to step file
    binvox_file: the binvox file ('chair.binvox' etc.)
    voxel_length: the length of one voxel
    voxel_width: the width of one voxel
    voxel_height: the height of one voxel
    application protocol: "AP203" or "AP214IS" or "AP242DIS"
    """
    with open(binvox_file, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)

    # initialize the STEP exporter
    step_writer = STEPControl_Writer()
    Interface_Static_SetCVal("write.step.schema", application_protocol)

    (position_x, position_y, position_z) = np.where(model.data)
    voxel = TopoDS_Compound()
    counter = TopoDS_Builder()
    counter.MakeCompound(voxel)

    for i in range(position_x.size):
        voxel1 = TopoDS_Shape(BRepPrimAPI_MakeBox(voxel_length, voxel_width, voxel_height).Shape())
        transmat = gp_Trsf()
        x, y, z = position_x[i] * voxel_length, position_y[i] * voxel_width, position_z[i] * voxel_height
        transmat.SetTranslation(gp_Vec(float(x), float(y), float(z)))
        location = TopLoc_Location(transmat)
        voxel1.Location(location)
        counter.Add(voxel, voxel1)

    # transfer shapes and write file
    step_writer.Transfer(voxel, STEPControl_AsIs)
    status = step_writer.Write(binvox_file[:-6]+"stp")
    if status != IFSelect_RetDone:
        raise AssertionError("load failed")


if __name__ == '__main__':
    binvox_to_step('bunny_32.binvox',10,10,10)
