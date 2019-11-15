# -*- coding: utf-8 -*-
# File: example.py
# Author: Arjit Jain <thearjitjain@gmail.com>
import SimpleITK as sitk

from slicerfiducials import SlicerFiducials

my_lmks_old = SlicerFiducials(name="BCD_Original.fcsv")
my_lmks_new = SlicerFiducials(name="BCD_Original_markup.fcsv",)

## Compute IPD
ipd = my_lmks_old.euclidean_distance("RE", "LE")
print("ipd is", ipd)

## compute difference between landmarks from two files
diff_lmks = SlicerFiducials.diff_files(my_lmks_old, my_lmks_new)
diff_lmks.write("diff.fcsv")

print(diff_lmks)

for name, point in iter(my_lmks_new):
    print(name)

## get a list of the landmark names
names = my_lmks_new.names()
print(names)

print("LE in physical space", my_lmks_old.query("LE"))
