#!/usr/bin/env python

from distutils.core import setup

setup(name='EOtools',
      version = '0.1',
      package_dir = {'EOtools' : 'src'},
      packages = ['EOtools','EOtools.DatasetDrivers','EOtools.stats'],
      author = 'Roger Edberg, Alex Ip, Josh Sixsmith',
      maintainer = 'Geoscience Australia',
      description = 'Collection of Earth Observation Tools.',
      long_description = 'Collection includes: DatasetDrivers, temporal statistics, array tiling.',
      license = 'BSD 3',
     )
