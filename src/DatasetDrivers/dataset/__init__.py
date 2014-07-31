"""
Various types of dataset used within DatasetDrivers and the image_processor. These are documented in their
respective submodules, but should be imported from here, not directly from those submodules.

:todo:
    These should be moved to the modules in which they are used. that is:

    - ElevationDataset -> DatasetDrivers.ancillary.elevation
    - OzoneDataset -> DatasetDrivers.ancillary.ozone
    - WaterVapourDataset -> DatasetDrivers.ancillary.water
    - SceneDataset -> DatasetDrivers
    - Dataset -> DatasetDrivers
"""

from _dataset import Dataset, DSException
from _scene_dataset import SceneDataset
