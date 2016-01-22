#!/usr/bin/env python

from __future__ import absolute_import

import geopandas
import numpy
from rasterio.crs import is_same_crs


def spatial_intersection(base_vector_fname, input_vector_fname, envelope=True):
    """
    Performs a spatial intersection of feature geometry to and
    returns a list of FID's from the base vector file.

    :param base_vector_fname:
        A string containing the full file path name to an
        OGR compliant vector file. This file will be used to select
        features from.

    :param input_vector_fname:
        A string containing the full file path name to an
        OGR compliant vector file.

    :param envelope:
        If set to True (Default), then the envelope of each feature
        will be used rather than the geometry of the feature to perform
        intersection.

    :return:
        A `list` containing the FID's of the base vector.
    """
    base_df = geopandas.read_file(base_vector_fname)
    input_df = geopandas.read_file(input_vector_fname)

    if not is_same_crs(base_df.crs, input_df.crs):
        input_df.to_crs(base_df.crs, inplace=True)

    wh = numpy.zeros((base_df.shape[0]), dtype='bool')

    # Not the most optimal solution, i.e. libspatialindex
    # but geopandas is quick enough just to loop over every feature
    if envelope:
        for feat in input_df.geometry:
            wh |= base_df.intersects(feat.envelope)
    else:
        for feat in input_df.geometry:
            wh |= base_df.intersects(feat)

    fids = base_df[wh].index.values.tolist()

    return fids


def retrieve_attribute_table(vector_fname):
    """
    Retrieves the attribute table for the input vector file.

    :param vector_fname:
        A string containing the full file path name to an
        OGR compliant vector file.

    :return:
        A `pandas.DataFrame` containing the attribute table.
    """
    df = geopandas.read_file(vector_fname)
    df.drop('geometry', axis=1, inplace=True)

    return df
