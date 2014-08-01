from __future__ import absolute_import
import numpy

# Author: Josh Sixsmith; joshua.sixsmith@ga.gov.au


def generate_tiles(samples, lines, xtile=100, ytile=100):
    """
    Generates a list of tile indices for a 2D array.

    :param samples:
        An integer expressing the total number of samples in an array.

    :param lines:
        An integer expressing the total number of lines in an array.

    :param xtile:
        (Optional) The desired size of the tile in the x-direction.
        Default is 100.

    :param ytile:
        (Optional) The desired size of the tile in the y-direction.
        Default is 100.

    :return:
        A list of tuples containing the precalculated tiles used for
        indexing a larger array.
        Each tuple contains (ystart,yend,xstart,xend).

    Example:

        >>> tiles = generate_tiles(8624, 7567, xtile=1000,ytile=400)
        >>>
        >>> for tile in tiles:
        >>>     ystart = int(tile[0])
        >>>     yend   = int(tile[1])
        >>>     xstart = int(tile[2])
        >>>     xend   = int(tile[3])
        >>>     xsize  = int(xend - xstart)
        >>>     ysize  = int(yend - ystart)
        >>>
        >>>     # When used to read data from disk
        >>>     subset = gdal_indataset.ReadAsArray(xstart, ystart, xsize, ysize)
        >>>
        >>>     # The same method can be used to write to disk.
        >>>     gdal_outdataset.WriteArray(array, xstart, ystart)
        >>>
        >>>     # Or simply move the tile window across an array
        >>>     subset = array[ystart:yend,xstart:xend] # 2D
        >>>     subset = array[:,ystart:yend,xstart:xend] # 3D
    """
    ncols = samples
    nrows = lines
    tiles = []
    xstart = numpy.arange(0, ncols, xtile)
    ystart = numpy.arange(0, nrows, ytile)
    for ystep in ystart:
        if ystep + ytile < nrows:
            yend = ystep + ytile
        else:
            yend = nrows
        for xstep in xstart:
            if xstep + xtile < ncols:
                xend = xstep + xtile
            else:
                xend = ncols
            tiles.append((ystep, yend, xstep, xend))
    return tiles
