from slicerfiducials import SlicerFiducials
import SimpleITK as sitk

fiducials = SlicerFiducials('./fids.fcsv')
image = sitk.ReadImage