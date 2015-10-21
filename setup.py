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
from distutils.core import setup

setup(name='eotools',
      version='0.5b',
      packages=[
            'eotools',
            'eotools.drivers',
            'eotools.metadata',
            'eotools.bodies',
      ],
      package_data={
            'eotools.drivers': ['_scene_dataset.xml'],
            'eotools.bodies': ['satellite.xml']
      },
      requires=[
            'numpy',
            'scipy',
            'gdal',
            'numexpr',
      ],
      author='Various',
      maintainer='Geoscience Australia',
      description='Collection of Earth Observation Tools.',
      long_description='Collection includes: dataset drivers, temporal statistics, array tiling.',
      license='BSD 3',
      )
