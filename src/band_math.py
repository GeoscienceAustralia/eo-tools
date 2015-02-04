#!/usr/bin/env python

from __future__ import absolute_import
import numexpr


def band_math(expression, variables_dict):
    """
    Evaluates a string math expression.
    Given a string expression and dictionary containing the variables
    declared within expression, evaluate the expression.

    :param expression:
        A string containing an expression.

    :param variables_dict:
        A dictionary containing the variables declared within the
        expression.

    :return:
        The evaluated expression. If the declared variables are ararys
        then an array of the same shape and type of the highest
        datatype will be returned.

    :example:
        >>> exp = "(b1 + b2) / 10.0"
        >>> a = numpy.random.randint(0, 256, (100, 100))
        >>> b = numpy.random.randint(0, 256, (100, 100))
        >>> d = {'b1': a, 'b2': b}
        >>> band_math(exp, d)
    """

    result = numexpr.evaluate(expression, local_dict=variables_dict)

    return result
