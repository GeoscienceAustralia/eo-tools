#!/usr/bin/env python

#===============================================================================
# Copyright (c)  2014 Geoscience Australia
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither Geoscience Australia nor the names of its contributors may be
#       used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================

import numpy

#Author: Josh Sixsmith; joshua.sixsmith@ga.gov.au

def generate_tiles(samples, lines, xtile=100, ytile=100, Generator=True):
    """
    Generates a list of tile indices for a 2D array.
    If Generator is set to True (Default), then a Python generator
    object will be returned rather than a list.

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

    :param Generator:
        A boolean indicating if a Python generator should be returned
        rather than a list.  True (Default) will return a Python
        generator object.

    :return:
        If Generator is set to True (Default), then a Python generator
        object will be returned. If set to False then a list of tuples
        containing the precalculated tiles used for indexing a larger
        array.
        Each tuple in the list or generator contains
        ((ystart,yend),(xstart,xend)).

    Example:

        >>> tiles = generate_tiles(8624, 7567, xtile=1000, ytile=400, Generator=False)
        >>>
        >>> for tile in tiles:
        >>>     ystart = int(tile[0][0])
        >>>     yend   = int(tile[0][1])
        >>>     xstart = int(tile[1][0])
        >>>     xend   = int(tile[1][1])
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
    def tiles_generator(samples, lines, xstart, ystart):
        """
        Creates a generator object for the tiles.
        """
        for ystep in ystart:
            if ystep + ytile < lines:
                yend = ystep + ytile
            else:
                yend = lines
            for xstep in xstart:
                if xstep + xtile < samples:
                    xend = xstep + xtile
                else:
                    xend = samples
                yield ((ystep,yend),(xstep, xend))

    def tiles_list(samples, lines, xstart, ystart):
        """
        Creates a list of tiles.
        """
        tiles = []
        for ystep in ystart:
            if ystep + ytile < lines:
                yend = ystep + ytile
            else:
                yend = lines
            for xstep in xstart:
                if xstep + xtile < samples:
                    xend = xstep + xtile
                else:
                    xend = samples
                tiles.append(((ystep,yend),(xstep, xend)))
        return tiles

    xstart = numpy.arange(0,samples,xtile)
    ystart = numpy.arange(0,lines,ytile)
    if Generator:
        return tiles_generator(samples, lines, xstart, ystart)
    else:
        return tiles_list(samples, lines, xstart, ystart)
