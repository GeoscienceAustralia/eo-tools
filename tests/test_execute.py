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

'''
Tests for the execute.py module.

Created on 02/09/2014

@author: u76345
'''

from __future__ import absolute_import
import unittest
from eotools.execute import execute


class TestExecute(unittest.TestCase):

    """Unit tests for the execute utility function."""

    def test_execute_echo(self):
        """Test the echo shell built-in command."""

        result = execute('echo "Hello"')

        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], 'Hello\n')
        self.assertEqual(result['stderr'], '')

    def test_execute_python(self):
        """Execute a python command as a list."""

        command = ['python',
                   '-c',
                   'print "Hello"'
                   ]
        result = execute(command, shell=False)

        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], 'Hello\n')
        self.assertEqual(result['stderr'], '')

    def test_execute_error(self):
        """Execute a python command causing an error."""

        command = ['python',
                   '-c',
                   'x = 1/0'
                   ]
        result = execute(command, shell=False)

        self.assertNotEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], '')
        self.assertRegexpMatches(result['stderr'], 'Traceback')
        self.assertRegexpMatches(result['stderr'], 'ZeroDivisionError')


def the_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [
        TestExecute
    ]

    suite_list = map(unittest.defaultTestLoader.loadTestsFromTestCase,
                     test_classes)

    suite = unittest.TestSuite(suite_list)

    return suite

#
# Run unit tests if in __main__
#

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(the_suite())
