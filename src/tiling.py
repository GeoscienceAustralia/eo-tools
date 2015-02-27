

# ===============================================================================
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
# ===============================================================================

from __future__ import absolute_import
import gdal
import numpy

# Author: Josh Sixsmith; joshua.sixsmith@ga.gov.au


def generate_tiles(samples, lines, xtile=100, ytile=100, generator=True):
    """
    Generates a list of tile indices for a 2D array.
    If generator is set to True (Default), then a Python generator
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

    :param generator:
        A boolean indicating if a Python generator should be returned
        rather than a list.  True (Default) will return a Python
        generator object.

    :return:
        If generator is set to True (Default), then a Python generator
        object will be returned. If set to False then a list of tuples
        containing the precalculated tiles used for indexing a larger
        array.
        Each tuple in the list or generator contains
        ((ystart,yend),(xstart,xend)).

    Example:

        >>> tiles = generate_tiles(8624, 7567, xtile=1000, ytile=400, generator=False)
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
                yield ((ystep, yend), (xstep, xend))

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
                tiles.append(((ystep, yend), (xstep, xend)))
        return tiles

    xstart = numpy.arange(0, samples, xtile)
    ystart = numpy.arange(0, lines, ytile)
    if generator:
        return tiles_generator(samples, lines, xstart, ystart)
    else:
        return tiles_list(samples, lines, xstart, ystart)


class TiledOutput:

    def __init__(self, out_fname, samples=None, lines=None, bands=1,
                 geobox=None, fmt="ENVI", nodata=None, dtype=gdal.GDT_Byte):
        """
        A class to aid in data processing using a tiling scheme.
        The `TiledOutput` class takes care of writing each tile/chunk
        of data to disk.

        :param out_fname:
            A string containing the full filepath name used for
            creating the image on disk.

        :param samples:
            An integer indicating the number of samples/columns contained
            in the entire image.

        :param lines:
            An integer indicating the number of lines/rows contained in
            the entire image.

        :param bands:
            The number of bands contained in the image. Default is 1.

        :param geobox:
            An instance of a GriddedGeoBox object.

        :param fmt:
            A GDAL compliant file format for the output image.

        :param nodata:
            The no data value for the image.

        :param dtype:
            An integer indicating datatype for the output image.
            Default is gdal.GDT_Byte which corresponds to 1.

        :example:
            >>> a = numpy.random.randint(0, 256, (1000, 1000)).astype('uint8')
            >>> tiles = generate_tiles(a.shape[1], a.shape[0], 100, 100, generator=False)
            (a - img).sum() == 0
            >>> len(tiles)
            100
            >>> outds = TiledOutput('test_tiled_output_2D', samples=a.shape[1], lines=a.shape[0])
            >>> outds.closed
            False
            >>> for tile in tiles:
            ...     ys, ye = tile[0]
            ...     xs, xe = tile[1]
            ...     subset = a[ys:ye, xs:xe]
            ...     outds.write_tile(subset, tile)
            ...
            >>> outds.close()
            >>> outds.closed
            True
            >>>
            >>> inds = gdal.Open('test_tiled_output_2D')
            >>> img = inds.ReadAsArray()
            >>> a.shape == img.shape
            True
            >>> (a - img).sum() == 0
            True
            >>> a = numpy.random.randint(0, 256, (10, 100, 100)).astype('uint8')
            outds.closed
            >>> tiles = generate_tiles(a.shape[2], a.shape[1], 10, 10, generator=False)
            >>> outds = TiledOutput('test_tiled_output_3D', samples=a.shape[2], lines=a.shape[1], bands=a.shape[0])
            for tile in tiles:
                ys, ye = tile[0]
                xs, xe = tile[1]
                subset = a[:, ys:ye, xs:xe]
                outds.write_tile(subset, tile)
            >>> outds.closed
            False
            >>> for tile in tiles:
            ...     ys, ye = tile[0]
            ...     xs, xe = tile[1]
            ...     subset = a[:, ys:ye, xs:xe]
            ...     outds.write_tile(subset, tile)
            ...
            outds.close()
            outds.closed
            inds = gdal.Open('test_tiled_output_3D')
            img = inds.ReadAsArray()
            a.shape == img.shape
            (a - img).sum() == 0
            >>> outds.close()
            >>> outds.closed
            True
            >>> inds = gdal.Open('test_tiled_output_3D')
            >>> img = inds.ReadAsArray()
            >>> a.shape == img.shape
            True
            >>> (a - img).sum() == 0
            True
        """

        # Check we have the correct dimensions to create the file
        if ((samples is None) or (lines is None)):
            msg = ("Samples and lines are required inputs! Samples: {ns} "
                   "Lines: {nl}").format(ns=samples, nl=lines)
            raise TypeError(msg)

        driver = gdal.GetDriverByName(fmt)
        self.outds = driver.Create(out_fname, samples, lines, bands, dtype)

        self.nodata = nodata
        self.geobox = geobox
        self.bands = bands

        self._set_geobox()
        self._set_bands_lookup()
        self._set_nodata()
        self.closed = False

    def _set_geobox(self):
        """
        Assign the georeference information (if we have any) to the output
        image.
        """
        if self.geobox is not None:
            transform = self.geobox.affine.to_gdal()
            projection = bytes(self.geobox.crs.ExportToWkt())

            self.outds.SetGeoTransform(transform)
            self.outds.SetProjection(projection)

    def _set_bands_lookup(self):
        """
        Define a dictionary that points to each raster band object on disk.
        Used for writing the actual data and setting items such as no data
        values.
        """
        out_bands = {}
        for i in range(1, self.bands + 1):
            out_bands[i] = self.outds.GetRasterBand(i)

        self.out_bands = out_bands

    def _set_nodata(self):
        """
        If we have a no data value, then assign it to the output file.
        """
        if self.nodata is not None:
            for i in range(1, self.bands + 1):
                self.out_bands[i].SetNoDataValue(self.nodata)

    def write_tile(self, array, tile, raster_band=None):
        """
        Given an array and tile index in the form:

            ((ystart, yend), (xstart, xend))

        and optionally a raster band, write the current tile to disk.
        The input `array` can be 2D or 3D. For the 2D case it is assumed
        that `array` will be written to the 1st raster bands unless
        specified by the parameter `raster_band`. For the 3D case it is
        assumed that `array` will have the dimensions (bands, rows, cols),
        whereby the number of bands will written to disk seqentially.
        The `raster_band` parameter will be ignored if `array` is 3D.
        """

        dims = array.ndim
        if array.ndim not in [2, 3]:
            msg = ("Input array is not 2 or 3 dimensions. "
                   "Array dimensions: {dims}").format(dims=dims)
            raise TypeError(msg)

        ystart = tile[0][0]
        xstart = tile[1][0]
        if dims == 3:
            for i in range(self.bands):
                band = i + 1
                self.out_bands[band].WriteArray(array[i], xstart, ystart)
                self.out_bands[band].FlushCache()
        else:
            band = 1 if raster_band is None else raster_band
            self.out_bands[band].WriteArray(array, xstart, ystart)
            self.out_bands[band].FlushCache()

    def close(self):
        """
        Close the output image and flush everything still in cache to disk.
        """

        for band in self.out_bands:
            self.out_bands[band] = None

        self.out_bands = None
        self.outds = None
        self.closed = True
