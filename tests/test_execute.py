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

'''
Tests for the execute.py module.

Created on 02/09/2014

@author: u76345
'''

from __future__ import absolute_import
import unittest
from EOtools.execute import execute


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
