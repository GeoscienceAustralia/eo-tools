#!/usr/bin/env python

# ===============================================================================
# Copyright 2015 Geoscience Australia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

from __future__ import absolute_import
import collections
from os.path import join as pjoin
import datetime
import numpy
from osgeo import gdal
from eotools.geobox import GriddedGeoBox
from eotools.tiling import generate_tiles
from eotools.tiling import TiledOutput
from eotools.bulk_stats import bulk_stats

gdal_2_numpy_dtypes = {1: 'uint8',
                       2: 'uint16',
                       3: 'int16',
                       4: 'uint32',
                       5: 'int32',
                       6: 'float32',
                       7: 'float64',
                       8: 'complex64',
                       9: 'complex64',
                       10: 'complex64',
                       11: 'complex128'}


class StackedDataset:

    """
    A class designed for dealing with datasets returned by stacker.py.
    The reason for only handling data returned by stacker.py are due to
    specific metadata references such as start_datetime and tile_pathname.

    File access to the image dataset is acquired upon request, for example
    when reading the image data.  Once the request has been made the file
    is closed.

    Example:

        >>> fname = 'FC_144_-035_BS.vrt'
        >>> ds = StackedDataset(fname)
        >>> # Get the number of bands associated with the dataset
        >>> ds.bands
        22
        >>> # Get the number of samples associated with the dataset
        >>> ds.samples
        4000
        >>> # Get the number of lines associated with the dataset
        >>> ds.lines
        4000
        >>> # Get the geotransform associated with the dataset
        >>> ds.geotransform
        (144.0, 0.00025000000000000017, 0.0, -34.0, 0.0, -0.00025000000000000017)
        >>> # Get the projection associated with the dataset
        >>> ds.projection
        'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,
        AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
        >>> # Initialise the yearly iterator
        >>> ds.init_yearly_iterator()
        >>> # Get the yearly iterator dictionary
        >>> ds.get_yearly_iterator()
        {1995: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            1996: [16, 17, 18, 19, 20, 21, 22]}
        >>> # Get the datetime of the first raster band
        >>> ds.get_raster_band_datetime()
        datetime.datetime(1995, 7, 2, 23, 19, 48, 452050)
        >>> # Get the metadata of the first raster band
        >>> ds.get_raster_band_metadata()
        {'start_datetime': '1995-07-02 23:19:48.452050', 'sensor_name': 'TM',
         'start_row': '83', 'end_row': '83', 'band_name': 'Bare Soil',
         'satellite_tag': 'LS5', 'cloud_cover': 'None', 'tile_layer': '3',
         'end_datetime': '1995-07-02 23:20:12.452050',
         'tile_pathname':
         '/g/data1/rs0/tiles/EPSG4326_1deg_0.00025pixel/LS5_TM/144_-035/1995/
          LS5_TM_FC_144_-035_1995-07-02T23-19-48.452050.tif',
         'gcp_count': '52', 'band_tag': 'BS', 'path': '94', 'level_name': 'FC',
         'y_index': '-35', 'x_index': '144', 'nodata_value': '-999'}
        >>> # Initialise the x & y block tiling sequence, using a block size
        >>> # of 400x by 400y
        >>> ds.init_tiling(400,400)
        >>> # Number of tiles
        >>> ds.n_tiles
        100
        >>> # Get the 11th tile (zero based index)
        >>> ds.get_tile(10)
        (400, 800, 0, 400)
        >>> # Read a single raster band. The 10th raster band (one based index)
        >>> img = ds.read_raster_band(10)
        >>> img.shape
        (4000, 4000)
        >>> # Read only a tile of a single raster band
        >>> # First tile, 10th raster band
        >>> img = ds.read_tile(ds.get_tile(0), 10)
        >>> img.shape
        (400, 400)
        >>> # Read all raster bands for the 24th tile
        >>> img = ds.read_tile_all_rasters(ds.get_tile(23))
        >>> img.shape
        (22, 400, 400)
    """

    def __init__(self, filename):
        """
        Initialise the class structure.

        :param file:
            A string containing the full filepath of a GDAL compliant
            dataset created by stacker.py.
        """

        self.fname = filename

        # Open the dataset
        ds = gdal.Open(filename)

        self.bands = ds.RasterCount
        self.samples = ds.RasterXSize
        self.lines = ds.RasterYSize

        self.projection = ds.GetProjection()
        self.geotransform = ds.GetGeoTransform()

        # Initialise the tile variables
        self.tiles = [None]
        self.n_tiles = 0
        self.init_tiling()

        # Get the no data value (assume the same value for all bands)
        band = ds.GetRasterBand(1)
        self.no_data = band.GetNoDataValue()

        # Close the dataset
        band = None
        ds = None

    def get_raster_band_metadata(self, raster_band=1):
        """
        Retrives the metadata for a given band_index.
        (Default is the first band).

        :param raster_band:
            The band index of interest. Default is the first band.

        :return:
            A dictionary containing band level metadata.
        """

        # Open the dataset
        ds = gdal.Open(self.fname)

        # Retrieve the band of interest
        band = ds.GetRasterBand(raster_band)

        # Retrieve the metadata
        metadata = band.GetMetadata()

        # Close the dataset
        band = None
        ds = None

        return metadata

    def get_raster_band_datetime(self, raster_band=1):
        """
        Retrieves the datetime for a given raster band index.

        :param raster_band:
            The raster band interest. Default is the first raster band.

        :return:
            A Python datetime object.
        """

        metadata = self.get_raster_band_metadata(raster_band)
        if 'start_datetime' in metadata:
            dt_item = metadata['start_datetime']
            try:
                str_fmt = "%Y-%m-%d %H:%M:%S.%f"
                start_dt = datetime.datetime.strptime(dt_item, str_fmt)
            except ValueError:
                try:
                    str_fmt = "%Y-%m-%d %H:%M:%S"
                    start_dt = datetime.datetime.strptime(dt_item, str_fmt)
                except ValueError:
                    raise
                    start_dt = None
            return start_dt
        else:
            return None

    def init_yearly_iterator(self):
        """
        Creates an interative dictionary containing all the band
        indices available for each year.
        """

        self.yearly_iterator = {}

        band_list = [1]  # Initialise to the first band
        dt_one = self.get_raster_band_datetime()
        if dt_one is not None:
            year_one = dt_one.year
            self.yearly_iterator[year_one] = band_list

            for i in range(2, self.bands + 1):
                year = self.get_raster_band_datetime(raster_band=i).year
                if year == year_one:
                    band_list.append(i)
                    self.yearly_iterator[year_one] = band_list
                else:
                    self.yearly_iterator[year_one] = band_list
                    year_one = year
                    band_list = [i]
        else:
            self.yearly_iterator[0] = range(1, self.bands + 1)

    def get_yearly_iterator(self):
        """
        Returns the yearly iterator dictionary created by init_yearly_iterator.
        """

        return self.yearly_iterator

    def init_tiling(self, xsize=None, ysize=None):
        """
        Sets the tile indices for a 2D array.

        :param xsize:
            Define the number of samples/columns to be included in a
            single tile.
            Default is the number of samples/columns.

        :param ysize:
            Define the number of lines/rows to be included in a single
            tile.
            Default is 10.

        :return:
            A list containing a series of tuples defining the
            individual 2D tiles/chunks to be indexed.
            Each tuple contains ((ystart, yend), (xstart, xend)).
        """
        if xsize is None:
            xsize = self.samples
        if ysize is None:
            ysize = 10
        self.tiles = generate_tiles(self.samples, self.lines, xtile=xsize,
                                    ytile=ysize, generator=False)
        self.n_tiles = len(self.tiles)

    def get_tile(self, index=0):
        """
        Retrieves a tile given an index.

        :param index:
            An integer containing the location of the tile to be used
            for array indexing.
            Defaults to the first tile.

        :return:
            A tuple containing the start and end array indices, of the
            form ((ystart, yend), (xstart, xend)).
        """

        tile = self.tiles[index]

        return tile

    def read_tile(self, tile, raster_bands=1):
        """
        Read an x & y block specified by tile for a given raster band
        or raster bands using GDAL.

        :param tile:
            A tuple containing the start and end array indices, of the
            form ((ystart, yend), (xstart,xend)).

        :param raster_bands:
            If reading from a single band, provide which raster band
            to read from. If raster_bands is a list, then it should
            contain the raster band numbers from which to read.
            Default is raster band 1.
        """

        ystart = int(tile[0][0])
        yend = int(tile[0][1])
        xstart = int(tile[1][0])
        xend = int(tile[1][1])
        xsize = int(xend - xstart)
        ysize = int(yend - ystart)

        # Open the dataset.
        ds = gdal.Open(self.fname)

        if isinstance(raster_bands, collections.Sequence):
            band = ds.GetRasterBand(1)
            dtype = gdal_2_numpy_dtypes[band.DataType]
            n_bands = len(raster_bands)
            subset = ds.ReadRaster(xstart, ystart, xsize, ysize,
                                   band_list=raster_bands)
            subset = numpy.frombuffer(subset, dtype=dtype).reshape(n_bands,
                                                                   ysize,
                                                                   xsize)
            ds.FlushCache()
            subset.flags['WRITEABLE'] = True
        else:
            band = ds.GetRasterBand(raster_bands)
            # Read the block and flush the cache (potentianl GDAL memory leak)
            subset = band.ReadAsArray(xstart, ystart, xsize, ysize)
            band.FlushCache()

        # Close the dataset
        band = None
        ds = None

        return subset

    def read_tile_all_rasters(self, tile):
        """
        Read an x & y block specified by tile from all raster bands
        using GDAL.

        :param tile:
            A tuple containing the start and end array indices, of the
            form ((ystart, yend), (xstart, xend)).
        """

        ystart = int(tile[0][0])
        yend = int(tile[0][1])
        xstart = int(tile[1][0])
        xend = int(tile[1][1])
        xsize = int(xend - xstart)
        ysize = int(yend - ystart)

        # Open the dataset.
        ds = gdal.Open(self.fname)

        # Read the array and flush the cache (potentianl GDAL memory leak)
        subset = ds.ReadAsArray(xstart, ystart, xsize, ysize)
        ds.FlushCache()

        # Close the dataset
        ds = None

        return subset

    def read_raster_band(self, raster_band=1):
        """
        Read the entire 2D block for a given raster band.
        By default the first raster band is read into memory.

        :param raster_band:
            The band index of interest. Default is the first band.

        :return:
            A NumPy 2D array of the same dimensions and datatype of
            the band of interest.
        """

        # Open the dataset.
        ds = gdal.Open(self.fname)

        band = ds.GetRasterBand(raster_band)
        array = band.ReadAsArray()

        # Flush the cache to prevent leakage
        band.FlushCache()

        # Close the dataset
        band = None
        ds = None

        return array

    def z_axis_stats(self, out_fname=None, raster_bands=None):
        """
        Compute statistics over the z-axis of the StackedDataset.
        An image containing 14 raster bands, each describing a
        statistical measure:

            * 1. Sum
            * 2. Mean
            * 3. Valid Observations
            * 4. Variance
            * 5. Standard Deviation
            * 6. Skewness
            * 7. Kurtosis
            * 8. Max
            * 9. Min
            * 10. Median (non-interpolated value)
            * 11. Median Index (zero based index)
            * 12. 1st Quantile (non-interpolated value)
            * 13. 3rd Quantile (non-interpolated value)
            * 14. Geometric Mean

        :param out_fname:
            A string containing the full file system path name of the
            image containing the statistical outputs.

        :param raster_bands:
            If raster_bands is None (Default) then statistics will be
            calculated across all bands. Otherwise raster_bands can be
            a list containing the raster bands of interest. This can be
            sequential or non-sequential.

        :return:
            An instance of StackedDataset referencing the stats file.
        """
        # Check if the image tiling has been initialised
        if self.n_tiles == 0:
            self.init_tiling()

        # Get the band names for the stats file
        band_names = ['Sum',
                      'Mean',
                      'Valid Observations',
                      'Variance',
                      'Standard Deviation',
                      'Skewness',
                      'Kurtosis',
                      'Max',
                      'Min',
                      'Median (non-interpolated value)',
                      'Median Index (zero based index)',
                      '1st Quantile (non-interpolated value)',
                      '3rd Quantile (non-interpolated value)',
                      'Geometric Mean']

        # out number of bands
        out_nb = 14

        # Construct the output image file to contain the result
        if out_fname is None:
            out_fname = pjoin(self.fname, '_z_axis_stats')

        geobox = GriddedGeoBox(shape=(self.lines, self.samples),
                               origin=(self.geotransform[0],
                                       self.geotransform[3]),
                               pixelsize=(self.geotransform[1],
                                          self.geotransform[5]),
                               crs=self.projection)

        outds = TiledOutput(out_fname, self.samples, self.lines, out_nb,
                            geobox, no_data=numpy.nan, dtype=gdal.GDT_Float32)

        # Write the band names
        for i in range(out_nb):
            outds.out_bands[i].SetDescription(band_names[i])

        # If we have None, set to read all bands
        if raster_bands is None:
            raster_bands = range(1, self.bands + 1)

        # Check that we have an iterable
        if not isinstance(raster_bands, collections.Sequence):
            msg = 'raster_bands is not a list but a {}'
            msg = msg.format(type(raster_bands))
            raise TypeError(msg)

        # Loop over every tile
        for tile_n in range(self.n_tiles):
            tile = self.get_tile(tile_n)
            subset = self.read_tile(tile, raster_bands)
            stats = bulk_stats(subset, no_data=self.no_data)
            outds.write_tile(stats, tile)

        outds.close()

        return StackedDataset(out_fname)
