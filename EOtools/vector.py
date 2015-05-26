#!/usr/bin/env python

import numpy
import ogr

def spatial_intersection(input_vector_fname, base_vector_fname, envelope=True):
    """
    Performs a spatial intersection of feature geometry to and
    returns a list of FID's from the base vector file.

    :param input_vector_fname:
        A string containing the full file path name to an
        OGR compliant vector file.

    :param base_vector_fname:
        A string containing the full file path name to an
        OGR compliant vector file. This file will be used to select
        features from.

    :param envelope:
        If set to True (Default), then the envelope of each feature
        will be used rather than the geometry of the feature to perform
        intersection.

    :return:
        A `list` containing the FID's of the base vector.
    """
    vec_ds1 = ogr.Open(input_vector_fname)
    vec_ds2 = ogr.Open(base_vector_fname)
    lyr1 = vec_ds1.GetLayer()
    lyr2 = vec_ds2.GetLayer()

    fids = []

    if envelope:
        for feat2 in lyr2:
            geom = feat2.GetGeometryRef()
            xmin, xmax, ymin, ymax = geom.GetEnvelope()
            lyr1.SetSpatialFilterRect(xmin, ymin, xmax, ymax)
            for feat1 in lyr1:
                fids.append(feat1.GetFID())
            lyr1.SetSpatialFilter(None)
    else:
        for feat2 in lyr2:
            ref = feat2.GetGeometryRef()
            lyr1.SetSpatialFilter(ref)
            for feat1 in lyr1:
                fids.append(feat1.GetFID())
            lyr1.SetSpatialFilter(None)

    fids = numpy.unique(numpy.array(fids)).tolist()

    return fids

