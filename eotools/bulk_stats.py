#!/usr/bin/env python

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
from __future__ import print_function
import numpy
import numexpr


def bulk_stats(array, no_data=None, double=False, as_bip=False):
    """
    Calculates statistics over the temporal/spectral/z domain
    of a multiband image.

    Calculates statistics over the temporal/spectral/z domain of an array
    containing [z,y,x] data.
    Statistics produced in this order are:
    Sum
    Valid Observations
    Mean
    Variance
    Standard Deviation
    Skewness
    Kurtosis
    Max
    Min
    Median (non-interpolated value)
    Median Index (zero based index)
    1st Quantile (non-interpolated value)
    3rd Quantile (non-interpolated value)
    Geometric Mean

    Median, 1st and 3rd quantiles: For odd length arrays the middle value is
    taken. For even length arrays, the first of the two middle values is taken.
    Either way, no interpolation is used for calculation.
    The median index is the band that the median value came from.

    The numexpr module is used to handle most of the operations. Arrays are
    processed faster while using less memory.
    The moments are calculated using the unbiased method i.e. (n - 1).
    The moments are also calculated direct via the formula rather than built
    in functions. Why?? Because we can recycle previous computations rather
    than recompute, which will make the routine faster.

    :param array:
        A 3D numpy array containing [z,y,x] data.

    :param no_data:
        The data value to ignore for calculations. Default is None.

    :param double:
        If set to True then `array` will be converted to float64 and
        the output will be evaluted in double precision and returned
        as such. Default is False (float32).

    :param as_bip:
        **Experimental**
        If set to True, the array will be transposed to be
        [Lines,Samples,Bands], and processed as such. The default
        is to process the array as [Bands,Lines,Samples], ie False.
        Experimental to see if the computations are quicker after
        transposing the data to be computed along the fastest
        memory access order. No difference maybe apparent as the
        transposed data will just be a view.

    Returns:
        A numpy float32 array, unless `double` is set to True,
        with NaN representing no data values.
    """

    # assuming a 3D array, [bands,rows,cols]
    dims = array.shape
    if len(dims) != 3:
        msg = "Array must be 3D! Received: {}.".format(len(dims))
        raise TypeError(msg)

    bands = dims[0]
    cols = dims[2]
    rows = dims[1]

    # number of bands/stats to be output to be returned
    output_band_count = 14

    # Define our computation datatype
    nan = numpy.float32(numpy.NaN)
    dtype = 'float32'
    if double:
        array = numpy.float64(array)
        nan = numpy.NaN
        dtype = 'float64'

    if no_data:
        wh = numexpr.evaluate("array == no_data")
        array[wh] = nan

    if as_bip:
        # a few transpositions will take place, but they are quick to create
        # and are mostly just views into the data, so no copies are made
        # !!!Hopefully!!!
        # The idea is that it will process the z-axis over the fastest
        # memory access order. But seeing as they're just views, it might not
        # have any effect.
        array_bip = numpy.transpose(array, (1, 2, 0))

        stats = numpy.zeros((output_band_count, rows, cols), dtype=dtype)

        # Sum
        stats[0] = numpy.nansum(array_bip, axis=2)

        # We need to keep an int for the valid observations
        vld_obsv = numpy.sum(numpy.isfinite(array_bip), axis=2)
        stats[2] = vld_obsv

        # Mean
        stats[1] = numexpr.evaluate("fsum / fvld_obsv",
                                    {'fsum': stats[0], 'fvld_obsv': stats[2]})

        residuals = numexpr.evaluate("array - mean", {'mean': stats[1],
                                                      'array': array})
        # Variance
        t_emp = numexpr.evaluate("residuals**2").transpose(1, 2, 0)
        nan_sum = numpy.nansum(t_emp, axis=2)
        stats[3] = numexpr.evaluate("nan_sum / (fvld_obsv - 1)",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # Stddev
        stats[4] = numexpr.evaluate("sqrt(var)", {'var': stats[3]})

        # Skewness
        t_emp = numexpr.evaluate("(residuals / stddev)**3",
                                 {'stddev': stats[4],
                                  'residuals': residuals}).transpose(1, 2, 0)
        nan_sum = numpy.nansum(t_emp, axis=2)
        stats[5] = numexpr.evaluate("nan_sum / fvld_obsv",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # Kurtosis
        t_emp = numexpr.evaluate("(residuals / stddev)**4",
                                 {'stddev': stats[4],
                                  'residuals': residuals}).transpose(1, 2, 0)
        nan_sum = numpy.nansum(t_emp, axis=2)
        stats[6] = numexpr.evaluate("(nan_sum / fvld_obsv) - 3",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # Max and Min
        stats[7] = numpy.nanmax(array_bip, axis=2)
        stats[8] = numpy.nanmin(array_bip, axis=2)

        # 2nd quantile (aka median)
        # Don't want any interpolated values, so can't use the standard
        # numpy.median() function
        # For odd length arrays, the middle value is taken, for even length
        # arrays, the first of the two middle values is taken

        # Sort the array
        flat_sort = numpy.sort(array_bip, axis=2).ravel()

        # q2_offset, median locations
        q2_idx = numexpr.evaluate("((vld_obsv / 2) + ((vld_obsv % 2) - 1))")

        # array offsets
        a_off = numpy.arange(cols * rows).reshape((rows, cols))

        # turn the locations into a useable 1D index
        idx_1D = numexpr.evaluate("(q2_idx + a_off * bands)").astype('int')
        stats[9] = flat_sort[idx_1D]  # get median values

        # now to find the original index of the median value
        sort_orig_idx = numpy.argsort(array_bip, axis=2).ravel()
        stats[10] = sort_orig_idx[idx_1D]

        # 1st quantile
        length = numexpr.evaluate("q2_idx + 1")
        q1_idx = numexpr.evaluate("((length / 2) + ((length % 2) - 1))")
        idx_1D = numexpr.evaluate("(q1_idx + a_off * bands)").astype('int')
        stats[11] = flat_sort[idx_1D]  # get 1st quantile

        # 3rd quantile
        exp = "((q2_idx + q1_idx) + a_off * bands)"
        idx_1D = numexpr.evaluate(exp).astype('int')  # 1D index
        stats[12] = flat_sort[idx_1D]  # get 3rd quantile

        # Geometric Mean
        # need to handle nan's so can't use scipy.stats.gmean ## 28/02/2013
        # x**(1./n) gives nth root
        wh = ~(numpy.isfinite(array_bip))
        array_bip[wh] = 1
        stats[13] = numpy.prod(array_bip, axis=2)**(1. / vld_obsv)

        # Any nan's will evaluate to 1.0, convert back to NaN
        wh = numexpr.evaluate("vld_obsv == 0")
        stats[13][wh] = nan

        # Convert any potential inf values to a NaN for consistancy
        wh = ~(numpy.isfinite(stats))
        stats[wh] = nan

    else:
        stats = numpy.zeros((output_band_count, rows, cols), dtype=dtype)

        # Sum
        stats[0] = numpy.nansum(array, axis=0)

        # We need to keep an int for the valid observations
        vld_obsv = numpy.sum(numpy.isfinite(array), axis=0)
        stats[2] = vld_obsv

        # Mean
        stats[1] = numexpr.evaluate("fsum / fvld_obsv",
                                    {'fsum': stats[0], 'fvld_obsv': stats[2]})

        residuals = numexpr.evaluate("array - mean",
                                     {'mean': stats[1], 'array': array})

        # Variance
        t_emp = numexpr.evaluate("residuals**2")
        nan_sum = numpy.nansum(t_emp, axis=0)
        stats[3] = numexpr.evaluate("nan_sum / (fvld_obsv - 1)",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # Stddev
        stats[4] = numexpr.evaluate("sqrt(var)", {'var': stats[3]})

        # skewness
        t_emp = numexpr.evaluate("(residuals / stddev)**3",
                                 {'stddev': stats[4], 'residuals': residuals})
        nan_sum = numpy.nansum(t_emp, axis=0)
        stats[5] = numexpr.evaluate("nan_sum / fvld_obsv",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # Kurtosis
        t_emp = numexpr.evaluate("(residuals / stddev)**4",
                                 {'stddev': stats[4], 'residuals': residuals})
        nan_sum = numpy.nansum(t_emp, axis=0)
        stats[6] = numexpr.evaluate("(nan_sum / fvld_obsv) - 3",
                                    {'fvld_obsv': stats[2],
                                     'nan_sum': nan_sum})

        # MAx and Min
        stats[7] = numpy.nanmax(array, axis=0)
        stats[8] = numpy.nanmin(array, axis=0)

        # 2nd quantile (aka median)
        # Don't want any interpolated values, so can't use the standard
        # numpy.median() function
        # For odd length arrays, the middle value is taken, for even length
        # arrays, the first of the two middle values is taken

        flat_sort = numpy.sort(array, axis=0).ravel()

        # q2_offset, median locations
        q2_idx = numexpr.evaluate("((vld_obsv / 2) + ((vld_obsv % 2) - 1))")

        # array offsets
        a_off = numpy.arange(cols * rows).reshape((rows, cols))

        # turn the locations into a useable 1D index
        exp = "(q2_idx * cols * rows + a_off)"
        idx_1D = numexpr.evaluate(exp).astype('int')
        stats[9] = flat_sort[idx_1D]  # get median values

        # now to find the original index of the median value
        sort_orig_idx = numpy.argsort(array, axis=0).ravel()
        stats[10] = sort_orig_idx[idx_1D]

        # 1st quantile
        length = numexpr.evaluate("q2_idx + 1")
        q1_idx = numexpr.evaluate("((length / 2) + ((length % 2) - 1))")
        exp = "(q1_idx * cols * rows + a_off)"
        idx_1D = numexpr.evaluate(exp).astype('int')  # 1D index
        stats[11] = flat_sort[idx_1D]  # get 1st quantile

        # 3rd quantile
        exp = "((q2_idx + q1_idx) * cols * rows + a_off)"
        idx_1D = numexpr.evaluate(exp).astype('int')  # 1D index
        stats[12] = flat_sort[idx_1D]  # get 3rd quantile

        # Geometric Mean
        # need to handle nan's so can't use scipy.stats.gmean ## 28/02/2013
        # x**(1./n) gives nth root
        wh = ~(numpy.isfinite(array))
        array[wh] = 1
        stats[13] = numpy.prod(array, axis=0)**(1. / vld_obsv)

        # Any nan's will evaluate to 1.0, convert back to NaN
        wh = numexpr.evaluate("vld_obsv == 0")
        stats[13][wh] = nan

        # Convert any potential inf values to a NaN for consistancy
        wh = ~(numpy.isfinite(stats))
        stats[wh] = nan

    return stats
