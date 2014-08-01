import numpy

#Author: Josh Sixsmith; joshua.sixsmith@ga.gov.au

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
    """
    ncols = samples
    nrows = lines
    tiles = []
    xstart = numpy.arange(0,ncols,xtile)
    ystart = numpy.arange(0,nrows,ytile)
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
            tiles.append((ystep,yend,xstep, xend))
    return tiles

