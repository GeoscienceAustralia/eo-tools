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

import unittest

import numpy.testing as npt
import numpy

from eotools.bulk_stats import bulk_stats
from scipy import stats


class TestStats(unittest.TestCase):

    """
    Unittests for the bulk_stats funtion.
    """

    def setUp(self):
        self.data = numpy.random.ranf((10, 100, 100))
        self.result = bulk_stats(self.data, double=True)


    def test_mean(self):
        """
        Test that the mean value is the same.
        """
        control = numpy.mean(self.data, axis=0)
        npt.assert_allclose(control, self.result[1])


    def test_variance(self):
        """
        Test that the variance is the same.
        """
        control = numpy.var(self.data, axis=0, ddof=1)
        npt.assert_allclose(control, self.result[3])


    def test_standard_deviation(self):
        """
        Test that the standard deviation is the same.
        """
        control = numpy.std(self.data, axis=0, ddof=1)
        npt.assert_allclose(control, self.result[4])


    def test_geometric_mean(self):
        """
        Test that the geometric mean is the same.
        """
        control = stats.gmean(self.data, axis=0)
        npt.assert_allclose(control, self.result[-1])


if __name__ == '__main__':
    npt.run_module_suite()
