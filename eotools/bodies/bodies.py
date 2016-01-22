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


"""
Calculations for satellite positions and various associated angles. This module needs some reqorking. It has
evolved through several refactorings and has become difficult to follow. Some of the function signatures are
out of date (i.e. they receive arguments that are either unused or could be simplified for the sake of clarity).
The docstrings are also out of date and consequently the documentation is currently incomplete or misleading.

:todo:
    Cleanup, rework, document and write tests for this module.
"""
from __future__ import absolute_import
import math


class earth(object):

    # Mean radius
    RADIUS = 6371009.0  # (metres)

    # WGS-84
    # RADIUS = 6378135.0  # equatorial (metres)
    # RADIUS = 6356752.0  # polar (metres)

    # Length of Earth ellipsoid semi-major axis (metres)
    SEMI_MAJOR_AXIS = 6378137.0

    # WGS-84
    A = 6378137.0           # equatorial radius (metres)
    B = 6356752.3142        # polar radius (metres)
    F = (A - B) / A         # flattening
    ECC2 = 1.0 - B**2 / A**2  # squared eccentricity

    MEAN_RADIUS = (A * 2 + B) / 3

    # Earth ellipsoid eccentricity (dimensionless)
    # ECCENTRICITY = 0.00669438
    # ECC2 = math.pow(ECCENTRICITY, 2)

    # Earth rotational angular velocity (radians/sec)
    OMEGA = 0.000072722052


def N(lat, sm_axis=earth.SEMI_MAJOR_AXIS, ecc2=earth.ECC2):
    lat_s = math.sin(lat)
    return sm_axis / math.sqrt(1.0 - ecc2 * lat_s * lat_s)


def geocentric_lat(lat_gd, sm_axis=earth.A, ecc2=earth.ECC2):
    """Convert geodetic latitude to geocentric latitude.

    Arguments:
        lat_gd: geodetic latitude (radians)
        sm_axis: Earth semi-major axis (metres)
        ecc2: Earth squared eccentricity (dimensionless)

    Returns:
        Geocentric latitude (radians)
    """
    # return math.atan((1.0 - ecc2) * math.tan(lat_gd))
    return math.atan2(math.tan(lat_gd), 1.0 / (1.0 - ecc2))


def geodetic_lat(lat_gc, sm_axis=earth.A, ecc2=earth.ECC2):
    """Calculate geocentric latitude to geodetic latitude.

    Arguments:
        lat_gc: geocentric latitude (radians)
        sm_axis: Earth semi-major axis (metres)
        ecc2: Earth squared eccentricity (dimensionless)

    Returns:
        Geodetic latitude (radians)
    """
    return math.atan2(math.tan(lat_gc), (1.0 - ecc2))


# These were found in 'earth.py', but appeared not be used
# def geocentric_lat(lat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     """Calculate geocentric latitude on the earth ellipsoid surface.
#
#     Arguments:
#         lat: geodetic latitude (radians)
#         sm_axis: length of earth ellipsoid semi-major axis (metres)
#         ecc2: squared eccentricity (dimensionless)
#
#     Returns:
#         Geocentric latitude value (radians).
#     """
#
#     lat_c = math.cos(lat)
#     lat_s = math.sin(lat)
#     N = sm_axis / math.sqrt(1.0 - ecc2 * lat_s * lat_s)
#     return lat - math.asin(N * ecc2 * lat_s * lat_c / sm_axis)
#
# def lat_geocentric(gdlat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     return math.atan((1.0 - ecc2) * math.tan(gdlat))
#
#
# def lat_geodetic(gclat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     return math.atan(math.tan(gclat) / (1.0 - ecc2))
