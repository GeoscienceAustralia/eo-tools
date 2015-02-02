#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import numpy


def pq_apply_dict():
    """
    Return a dictionary containing boolean values on whether or not
    to apply a PQ quality flag.
    """

    d = {'Saturation_1': True,
         'Saturation_2': True,
         'Saturation_3': True,
         'Saturation_4': True,
         'Saturation_5': True,
         'Saturation_61': True,
         'Saturation_62': True,
         'Saturation_7': True,
         'Contiguity': True,
         'Land_Sea': True,
         'ACCA': True,
         'Fmask': True,
         'CloudShadow_1': True,
         'CloudShadow_2': True,
         'Empty_1': False,
         'Empty_2': False
         }

    return d


def pq_apply_invert_dict():
    """
    Return a dictionary containing boolean values on whether or not
    to apply a PQ quality flag inversely.
    """

    d = {'Saturation_1': False,
         'Saturation_2': False,
         'Saturation_3': False,
         'Saturation_4': False,
         'Saturation_5': False,
         'Saturation_61': False,
         'Saturation_62': False,
         'Saturation_7': False,
         'Contiguity': False,
         'Land_Sea': False,
         'ACCA': False,
         'Fmask': False,
         'CloudShadow_1': False,
         'CloudShadow_2': False,
         'Empty_1': False,
         'Empty_2': False
         }

    return d


def extract_pq_flags(array, flags=None, invert=None, check_zero=False,
                     combine=False):
    """
    Extracts pixel quality flags from the pixel quality bit array.

    :param array:
        A NumPy 2D or 3D array containing the PQ bit array. If array
        is 3D, then combine is set to True.

    :param flags:
        A dictionary containing each PQ flag and a boolean value
        determining if that flag is to be extracted.
        If None; then this routine will get the default PQ flags dictionary
        which is True for all flags.

    :param invert:
        A dictionary containing each PQ flag and a boolean value
        determining if that flag is to be inverted once extracted.
        Useful if you want to investigate that pheonomena.
        If None; then this routine will get the default invert flags dictionary
        which is False for all flags.

    :param check_zero:
        A boolean keyword as to whether or not the PQ bit array should
        be checked for instances of zero prior to bit extraction.
        Ideally this should be set when investigating specific
        pheonomena. Default is False.

    :param combine:
        A boolean keyword as to whether or not the extracted PQ masks
        should be combined into a single mask. If input array is 3D,
        then combine is set to True.

    :return:
        An n-D NumPy array of type bool where n is given by the number
        of flags present in the flags dictionary. If combine is set
        then a single 2D NumPy array of type bool is returned. If
        the input array is 3D, then combine is set to True and PQ is
        extracted for every `band` in [band, row, column].

    :notes:
        If either the flags or invert dictionaries contain incorrect
        keys, then they will be reported and ignored during bit
        extraction.

    Example:

        >>> # This will automatically get the default PQ and inversion flags
        >>> # and combine the result into a single boolean array
        >>> pq = pq_utils.extract_pq_flags(img, check_zero=True, combine=True)
        >>> # For this example, we'll only extract the cloud flags, invert them
        >>> # so we only have the cloud data, and combine them into a single
        >>> # boolean array
        >>> d = pq_utils.pq_apply_invert_dict()
        >>> # The PQapplyInvertDict() returns False for every flag
        >>> d['ACCA'] = True
        >>> d['Fmask'] = True
        >>> pq = pq_utils.extract_pq_flags(img, check_zero=True, combine=True, invert=d, flags=d)
    """

    # Check for existance of flags
    if flags is None:
        flags = pq_apply_dict()
    elif not isinstance(flags, dict):
        print("flags must be of type dict. Retrieving default PQ flags dict.")
        flags = pq_apply_dict()

    # Check for existance of invert
    if invert is None:
        invert = pq_apply_invert_dict()
    elif not isinstance(invert, dict):
        print("invert must be of type dict. Retrieving default PQ invert dict.")
        invert = pq_apply_invert_dict()

    # Check for correct dimensionality
    if not ((array.ndim != 2) or (array.ndim != 3)):
        msg = 'Error. Array dimensions must be 2D or 3D, not {}'
        msg = msg.format(array.ndim)
        raise Exception(msg)

    # image dimensions
    dims = array.shape
    if array.ndim == 3:
        samples = dims[2]
        lines = dims[1]
        bands = dims[0]
        combine = True
    else:
        samples = dims[1]
        lines = dims[0]

    # Initialise the PQ flag bit positions
    bit_shift = {'Saturation_1': {'value': 1, 'bit': 0},
                 'Saturation_2': {'value': 2, 'bit': 1},
                 'Saturation_3': {'value': 4, 'bit': 2},
                 'Saturation_4': {'value': 8, 'bit': 3},
                 'Saturation_5': {'value': 16, 'bit': 4},
                 'Saturation_61': {'value': 32, 'bit': 5},
                 'Saturation_62': {'value': 64, 'bit': 6},
                 'Saturation_7': {'value': 128, 'bit': 7},
                 'Contiguity': {'value': 256, 'bit': 8},
                 'Land_Sea': {'value': 512, 'bit': 9},
                 'ACCA': {'value': 1024, 'bit': 10},
                 'Fmask': {'value': 2048, 'bit': 11},
                 'CloudShadow_1': {'value': 4096, 'bit': 12},
                 'CloudShadow_2': {'value': 8192, 'bit': 13},
                 'Empty_1': {'value': 16384, 'bit': 14},
                 'Empty_2': {'value': 32768, 'bit': 15}
                 }

    bits = []
    values = []
    invs = []
    # Check for correct keys in dicts
    for k, v in flags.items():
        if (k in bit_shift) and (k in invert) and v:
            values.append(bit_shift[k]['value'])
            bits.append(bit_shift[k]['bit'])
            invs.append(invert[k])
        else:
            print("Skipping PQ flag {}".format(k))

    # sort via bits
    container = sorted(zip(bits, values, invs))

    nflags = len(container)

    # Extract PQ flags
    if check_zero:
        zero = array == 0
        if combine:
            # When combining we need to turn pixels to False, therefore
            # we initialise as True:
            #     True & True = True
            #     True & False =  False
            #     False & True = False
            #     False & False = False
            mask = numpy.ones(dims, dtype='bool')
            for b, v, i in container:
                if i:
                    mask &= ~((array & v) >> b).astype('bool')
                else:
                    mask &= (array & v) >> b
            # Account for zero during bit extraction
            mask[zero] = True
        else:
            mask = numpy.zeros((nflags, lines, samples), dtype='bool')
            for idx, [b, v, i] in enumerate(container):
                if i:
                    mask[idx] = ~((array & v) >> b).astype('bool')
                else:
                    mask[idx] = (array & v) >> b
            mask[:, zero] = True
    else:
        if combine:
            # When combining we need to turn pixels to False, therefore
            # we initialise as True:
            #     True & True = True
            #     True & False =  False
            #     False & True = False
            #     False & False = False
            mask = numpy.ones(dims, dtype='bool')
            for b, v, i in container:
                if i:
                    mask &= ~((array & v) >> b).astype('bool')
                else:
                    mask &= (array & v) >> b
        else:
            mask = numpy.zeros((nflags, lines, samples), dtype='bool')
            for idx, [b, v, i] in enumerate(container):
                if i:
                    mask[idx] = ~((array & v) >> b).astype('bool')
                else:
                    mask[idx] = (array & v) >> b

    return mask
