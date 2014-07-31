#!/usr/bin/env python

import os
import datetime
import numpy
from osgeo import gdal
from image_tools import get_tiles

def PQapplyDict():
    """
    Return a dictionary containing boolean values on whether or not
    to apply a PQ quality flag.
    """

    d = {'Saturation_1'  : True,
         'Saturation_2'  : True,
         'Saturation_3'  : True,
         'Saturation_4'  : True,
         'Saturation_5'  : True,
         'Saturation_61' : True,
         'Saturation_62' : True,
         'Saturation_7'  : True,
         'Contiguity'    : True,
         'Land_Sea'      : True,
         'ACCA'          : True,
         'Fmask'         : True,
         'CloudShadow_1' : True,
         'CloudShadow_2' : True,
         'Empty_1'       : False,
         'Empty_2'       : False
        }

    return d

def PQapplyInvertDict():
    """
    Return a dictionary containing boolean values on whether or not
    to apply a PQ quality flag inversely.
    """

    d = {'Saturation_1'  : False,
         'Saturation_2'  : False,
         'Saturation_3'  : False,
         'Saturation_4'  : False,
         'Saturation_5'  : False,
         'Saturation_61' : False,
         'Saturation_62' : False,
         'Saturation_7'  : False,
         'Contiguity'    : False,
         'Land_Sea'      : False,
         'ACCA'          : False,
         'Fmask'         : False,
         'CloudShadow_1' : False,
         'CloudShadow_2' : False,
         'Empty_1'       : False,
         'Empty_2'       : False
        }

    return d

def extractPQFlags(array, flags=None, invert=None, check_zero=False, combine=False):
    """
    Extracts pixel quality flags from the pixel quality bit array.

    :param array:
        A NumPy 2D array containing the PQ bit array.

    :param flags:
        A dictionary containing each PQ flag and a boolean value
        determining if that flag is to be extracted.

    :param invert:
        A dictionary containing each PQ flag and a boolean value
        determining if that flag is to be inverted once extracted.
        Useful if you want to investigate that pheonomena.

    :param check_zero:
        A boolean keyword as to whether or not the PQ bit array should
        be checked for instances of zero prior to bit extraction.
        Ideally this should be set when investigating specific
        pheonomena. Default is False.

    :param combine:
        A boolean keyword as to whether or not the extracted PQ masks
        should be combined into a single mask.

    :return:
        An n-D NumPy array of type bool where n is given by the number
        of flags present in the flags dictionary. If combine is set
        then a single 2D NumPy array of type bool is returned.

    :notes:
        If either the flags or invert dictionaries contain incorrect
        keys, then they will be reported and ignored during bit
        extraction.
    """

    # Check for existance of flags 
    if flags is None:
        flags = PQapplyDict()
    elif type(flags) != dict:
        print "flags must be of type dict. Retrieving default PQ flags dict."
        flags = PQapplyDict()

    if array.ndim != 2:
        raise Exception('Error. Array dimensions must be 2D, not %i' %array.ndim)

    # image dimensions
    dims = array.shape
    samples = dims[1]
    lines   = dims[0]

    # Initialise the PQ flag bit positions
    bit_shift = {'Saturation_1'  : {'value' : 1,     'bit' : 0},
                 'Saturation_2'  : {'value' : 2,     'bit' : 1},
                 'Saturation_3'  : {'value' : 4,     'bit' : 2},
                 'Saturation_4'  : {'value' : 8,     'bit' : 3},
                 'Saturation_5'  : {'value' : 16,    'bit' : 4},
                 'Saturation_61' : {'value' : 32,    'bit' : 5},
                 'Saturation_62' : {'value' : 64,    'bit' : 6},
                 'Saturation_7'  : {'value' : 128,   'bit' : 7},
                 'Contiguity'    : {'value' : 256,   'bit' : 8},
                 'Land_Sea'      : {'value' : 512,   'bit' : 9},
                 'ACCA'          : {'value' : 1024,  'bit' : 10},
                 'Fmask'         : {'value' : 2048,  'bit' : 11},
                 'CloudShadow_1' : {'value' : 4096,  'bit' : 12},
                 'CloudShadow_2' : {'value' : 8192,  'bit' : 13},
                 'Empty_1'       : {'value' : 16384, 'bit' : 14},
                 'Empty_2'       : {'value' : 32768, 'bit' : 15}
                }

    bits   = []
    values = []
    invs   = []
    # Check for correct keys in dicts
    for k, v in flags.items():
        if (k in bit_shift) and (k in invert) and v:
           values.append(bit_shift[k]['value'])
           bits.append(bit_shift[k]['bit'])
           invs.append(invert[k])
        else:
            print "Skipping PQ flag %s"%k

    # sort via bits
    container = sorted(zip(bits, values, invs))

    nflags = len(container)

    # Extract PQ flags
    if check_zero:
        zero = array == 0
        if combine:
            mask = numpy.zeros(dims, dtype='bool')
            for b, v, i in container:
                if i:
                    mask &= ~((array & v) >> b).astype('bool')
                else:
                    mask &= (array & v) >> b
            # Account for zero during bit extraction
            mask[zero] = True
        else:
            mask = numpy.zeros((nflags, lines, samples), dtype='bool')
            for idx, [b,v,i] in enumerate(container):
                if i:
                    mask[idx] = ~((array & v) >> b).astype('bool')
                else:
                    mask[idx] = (array & v) >> b
            mask[:,zero] = True
    else:
        if combine:
            mask = numpy.zeros(dims, dtype='bool')
            for b, v, i in container:
                if i:
                    mask &= ~((array & v) >> b).astype('bool')
                else:
                    mask &= (array & v) >> b
        else:
            mask = numpy.zeros((nflags, lines, samples), dtype='bool')
            for idx, [b,v,i] in enumerate(container):
                if i:
                    mask[idx] = ~((array & v) >> b).astype('bool')
                else:
                    mask[idx] = (array & v) >> b

    return mask


class StackerDataset:
    """
    A class designed for dealing with datasets returned by stacker.py.
    The reason for only handling data returned by stacker.py are due to 
    specific metadata references such as start_datetime and tile_pathname.

    File access to the image dataset is acquired upon request, for example
    when reading the image data.  Once the request has been made the file
    is closed.

    Example:

        >>> fname = 'FC_144_-035_BS.vrt'
        >>> ds = StackerDataset(fname)
        >>> # Get the number of bands associated with the dataset
        >>> ds.bands
        22
        >>> # Get the number of samples associated with the dataset
        >>> ds.samples
        4000
        >>> # Get the number of lines associated with the dataset
        >>> ds.lines
        4000
        >>> # Initialise the yearly iterator
        >>> ds.initYearlyIterator()
        >>> # Get the yearly iterator dictionary
        >>> ds.getYearlyIterator()
        {1995: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            1996: [16, 17, 18, 19, 20, 21, 22]}
        >>> # Get the datetime of the first raster band
        >>> ds.getRasterBandDatetime()
        datetime.datetime(1995, 7, 2, 23, 19, 48, 452050)
        >>> # Get the metadata of the first raster band
        >>> ds.getRasterBandMetadata()
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
        >>> ds.initTiling(400,400)
        >>> # Number of tiles
        >>> ds.nTiles
        100
        >>> # Get the 11th tile (zero based index)
        >>> ds.getTile(10)
        (400, 800, 0, 400)
        >>> # Read a single raster band. The 10th raster band (one based index)
        >>> img = ds.readRasterBand(10)
        >>> img.shape
        (4000, 4000)
        >>> # Read only a tile of a single raster band
        >>> # First tile, 10th raster band
        >>> img = ds.readTile(ds.getTile(0), 10)
        >>> img.shape
        (400, 400)
        >>> # Read all raster bands for the 24th tile
        >>> img = ds.readTileAllRasters(ds.getTile(23))
        >>> img.shape
        (22, 400, 400)
    """

    def __init__(self, filename):
        """
        Initialise the class structure.

        :param file:
            A string containing the full filepath of a GDAL compliant dataset created by stacker.py.
        """

        self.fname = filename

        # Open the dataset
        ds = gdal.Open(filename)

        self.bands   = ds.RasterCount
        self.samples = ds.RasterXSize
        self.lines   = ds.RasterYSize

        # Initialise the tile variables
        self.tiles  = [None]
        self.nTiles = 0

        # Close the dataset
        ds = None

    def getRasterBandMetadata(self, raster_band=1):
        """
        Retrives the metadata for a given band_index. (Default is the first band).

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
        ds = None

        return metadata

    def getRasterBandDatetime(self, raster_band=1):
        """
        Retrieves the datetime for a given raster band index.

        :param raster_band:
            The raster band interest. Default is the first raster band.

        :return:
            A Python datetime object.
        """

        metadata = self.getRasterBandMetadata(raster_band)
        dt_item  = metadata['start_datetime']
        start_dt = datetime.datetime.strptime(dt_item, "%Y-%m-%d %H:%M:%S.%f")

        return start_dt

    def initYearlyIterator(self):
        """
        Creates an interative dictionary containing all the band indices available for each year.
        """

        self.yearlyIterator = {}

        band_list = [1] # Initialise to the first band
        yearOne   = self.getRasterBandDatetime().year

        self.yearlyIterator[yearOne] = band_list

        for i in range(2, self.bands + 1):
            year = self.getRasterBandDatetime(raster_band=i).year
            if year == yearOne:
                band_list.append(i)
                self.yearlyIterator[yearOne] = band_list
            else:
                self.yearlyIterator[yearOne] = band_list
                yearOne = year
                band_list = [i]

    def getYearlyIterator(self):
        """
        Returns the yearly iterator dictionary created by setYearlyIterator.
        """

        return self.yearlyIterator

    def initTiling(self, xsize=100, ysize=100):
        """
        Sets the tile indices for a 2D array.

        :param xsize:
            Define the number of samples/columns to be included in a single tile.
            Default is 100

        :param ysize:
            Define the number of lines/rows to be included in a single tile.
            Default is 100.

        :return:
            A list containing a series of tuples defining the individual 2D tiles/chunks to be indexed.
            Each tuple contains (ystart,yend,xstart,xend).
        """

        self.tiles  = get_tiles(self.samples, self.lines, xtile=xsize,ytile=ysize)
        self.nTiles = len(self.tiles)

    def getTile(self, index=0):
        """
        Retrieves a tile given an index.

        :param index:
            An integer containing the location of the tile to be used for array indexing.
            Defaults to the first tile.

        :return:
            A tuple containing the start and end array indices, of the form (ystart,yend,xstart,xend).
        """

        tile = self.tiles[index]

        return tile

    def readTile(self, tile, raster_band=1):
        """
        Read an x & y block specified by tile for a given raster band using GDAL.

        :param tile:
            A tuple containing the start and end array indices, of the form
            (ystart,yend,xstart,xend).

        :param raster_band:
            If reading from a single band, provide which raster band to read from.
            Default is raster band 1.
        """

        ystart = int(tile[0])
        yend   = int(tile[1])
        xstart = int(tile[2])
        xend   = int(tile[3])
        xsize  = int(xend - xstart)
        ysize  = int(yend - ystart)

        # Open the dataset.
        ds = gdal.Open(self.fname)

        band = ds.GetRasterBand(raster_band)

        # Read the block and flush the cache (potentianl GDAL memory leak)
        subset = band.ReadAsArray(xstart, ystart, xsize, ysize)
        band.FlushCache()

        # Close the dataset
        ds = None

        return subset

    def readTileAllRasters(self, tile):
        """
        Read an x & y block specified by tile from all raster bands
        using GDAL.

        :param tile:
            A tuple containing the start and end array indices, of the form
            (ystart,yend,xstart,xend).
        """

        ystart = int(tile[0])
        yend   = int(tile[1])
        xstart = int(tile[2])
        xend   = int(tile[3])
        xsize  = int(xend - xstart)
        ysize  = int(yend - ystart)

        # Open the dataset.
        ds = gdal.Open(self.fname)

        # Read the array and flush the cache (potentianl GDAL memory leak)
        subset = ds.ReadAsArray(xstart, ystart, xsize, ysize)
        ds.FlushCache()

        # Close the dataset
        ds = None

        return subset

    def readRasterBand(self, raster_band=1):
        """
        Read the entire 2D block for a given raster band.
        By default the first raster band is read into memory.

        :param raster_band:
            The band index of interest. Default is the first band.

        :return:
            A NumPy 2D array of the same dimensions and datatype of the band of interest.
        """

        # Open the dataset.
        ds = gdal.Open(self.fname)

        band  = ds.GetRasterBand(raster_band)
        array = band.ReadAsArray()

        # Flush the cache to prevent leakage
        band.FlushCache()

        # Close the dataset
        ds = None

        return array

