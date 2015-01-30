#!/usr/bin/env python

from __future__ import absolute_import
import collections
import numpy
from scipy.ndimage import map_coordinates

from EOtools.coordinates import convert_coordinates
from EOtools.DatasetDrivers.stackerDataset import StackerDataset


def x_profile(stacker_dataset, xy, raster_band=1, from_map=False):
    """
    Get the data associated with the x-axis of an image.

    :param stacker_dataset:
        An instance of a StackerDataset.

    :param xy:
        An tuple containing an (x, y) co-ordinate pair from which to
        read the horizontal profile.

    :param raster_band:
        The raster band to read from. Default is raster band 1.

    :param from_map:
        A boolean indicating whether or not the input co-ordinates
        are real world map coordinates. If set to True, then the input
        xy co-ordinate will be converted to image co-ordinates.

    :return:
        A 1D NumPy array of length determined by the number of columns
        in the stacker_dataset.
    """
    if not isinstance(stacker_dataset, StackerDataset):
        msg = ('stacker_dataset should be an instance of StackerDataset but '
               'is of type {}')
        msg = msg.format(type(stacker_dataset))
        raise TypeError(msg)

    # Convert to image co-ordinates if needed
    if from_map:
        x, y = convert_coordinates(stacker_dataset.geotransform, xy,
                                   to_map=False)
    else:
        x, y = xy

    # Create a tile to define the chunk we wish to read
    tile = ((y, y + 1), (0, stacker_dataset.samples))

    # Read the profile
    profile = stacker_dataset.read_tile(tile, raster_bands=raster_band)

    return profile[0, :]


def y_profile(stacker_dataset, xy, raster_band=1, from_map=False):
    """
    Get the data associated with a y-axis of an image.

    :param stacker_dataset:
        An instance of a StackerDataset.

    :param xy:
        An tuple containing an (x, y) co-ordinate pair from which to
        read the vertical profile.

    :param raster_band:
        The raster band to read from. Default is raster band 1.

    :param from_map:
        A boolean indicating whether or not the input co-ordinates
        are real world map coordinates. If set to True, then the input
        xy co-ordinate will be converted to image co-ordinates.

    :return:
        A 1D NumPy array of length determined by the number of rows in
        the stacker_dataset.
    """
    if not isinstance(stacker_dataset, StackerDataset):
        msg = ('stacker_dataset should be an instance of StackerDataset but '
               'is of type {}')
        msg = msg.format(type(stacker_dataset))
        raise TypeError(msg)

    # Convert to image co-ordinates if needed
    if from_map:
        x, y = convert_coordinates(stacker_dataset.geotransform, xy,
                                   to_map=False)
    else:
        x, y = xy

    # Create a tile to define the chunk we wish to read
    tile = ((0, stacker_dataset.lines), (x, x + 1))

    # Read the profile
    profile = stacker_dataset.read_tile(tile, raster_bands=raster_band)

    return profile[:, 0]


def z_profile(stacker_dataset, xy, from_map=False, raster_bands=None):
    """
    Get the data associated with the z-axis of an image.
    The z-axis for a 3D image is also known as a spectral profile for
    spectrally stacked data or a temporal profile for temporally
    stacked data.

    :param stacker_dataset:
        An instance of a StackerDataset.

    :param xy:
        The xy co-ordinate from which to get the z profile.

    :param from_map:
        A boolean indicating whether or not the input co-ordinates
        are real world map coordinates. If set to True, then the input
        xy co-ordinate will be converted to image co-ordinates.

    :return:
        A 1D NumPy array of length determined by the number of raster
        bands in the stacker_dataset.
    """
    if not isinstance(stacker_dataset, StackerDataset):
        msg = ('stacker_dataset should be an instance of StackerDataset but '
               'is of type {}')
        msg = msg.format(type(stacker_dataset))
        raise TypeError(msg)

    # Convert to image co-ordinates if needed
    if from_map:
        x, y = convert_coordinates(stacker_dataset.geotransform, xy,
                                   to_map=False)
    else:
        x, y = xy

    # Create a tile to define the chunk we wish to read
    tile = ((y, y + 1), (x, x + 1))

    if ((raster_bands is None) or
            (not isinstance(raster_bands, collections.Sequence))):
        nb = range(1, stacker_dataset.bands + 1)
    else:
        nb = raster_bands

    # Read the profile
    profile = stacker_dataset.read_tile(tile, raster_bands=nb)

    return profile[:, 0, 0]


def arbitrary_profile(stacker_dataset, xy_points, raster_band=1,
                      cubic=False, from_map=False):
    """
    Get the data associated with an arbitrary set of points that
    define an arbitrary profile/transect, and the pixel locations
    associated with the transect.

    :param stacker_dataset:
        An instance of a StackerDataset.

    :param xy_points:
        A list of (x, y) co-ordinate paris eg [(x, y), (x, y), (x, y)].

    :param raster_band:
        The raster band to read from. Default is raster band 1.

    :param from_map:
        A boolean indicating whether or not the input co-ordinates
        are real world map coordinates. If set to True, then the input
        xy co-ordinate will be converted to image co-ordinates.

    :return:
        A 1D NumPy array of lenght determined by the distance between
        the xy_points; A tuple (y_index, x_index) containing the
        pixel locations of the transect; and a tuple containing a list
        of start and end co-ordinates for both x and y fields.
        The form of the start and end locations is:

            ([(xstart_1, xend_1),...,(xstart_n-1, xend_n-1)],
             [(ystart_1, yend_1),...,(ystart_n-1, yend_n-1)]).

        This form can be directly used in a call to plot() as follows:

            z_prf, idx, xy_start_end = arbitrary_profile()
            plot(xy_start_end[0], xy_start_end[1], 'r-')
    """
    if not isinstance(stacker_dataset, StackerDataset):
        msg = ('stacker_dataset should be an instance of StackerDataset but '
               'is of type {}')
        msg = msg.format(type(stacker_dataset))
        raise TypeError(msg)

    n_points = len(xy_points)
    if n_points < 2:
        msg = "Minimum number of points is 2, received {}".format(n_points)
        raise ValueError(msg)

    # Convert to image co-ordinates if needed
    if from_map:
        img_xy = convert_coordinates(stacker_dataset.geotransform, xy_points,
                                     to_map=False)
    else:
        img_xy = xy_points

    # Read the image band
    img = stacker_dataset.read_raster_band(raster_band=raster_band)

    profile = numpy.array([], dtype=img.dtype)
    x_idx = numpy.array([], dtype='int')
    y_idx = numpy.array([], dtype='int')
    x_start_end = []
    y_start_end = []
    for i in range(1, n_points):
        x0, y0 = img_xy[i - 1]
        x1, y1 = img_xy[i]
        x_start_end.append((x0, x1))
        y_start_end.append((y0, y1))

        n_pixels = max(abs(x1 - x0 + 1), abs(y1 - y0 + 1))
        x = numpy.linspace(x0, x1, n_pixels)
        y = numpy.linspace(y0, y1, n_pixels)
        x_idx = numpy.append(x_idx, x)
        y_idx = numpy.append(y_idx, y)

        if cubic:
            transect = map_coordinates(img, (y, x))
            profile = numpy.append(profile, transect)
        else:
            transect = img[y.astype('int'), x.astype('int')]
            profile = numpy.append(profile, transect)

    x_idx = x_idx.astype('int')
    y_idx = y_idx.astype('int')

    return (profile, (y_idx, x_idx), (x_start_end, y_start_end))
