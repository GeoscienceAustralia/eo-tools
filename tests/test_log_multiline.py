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
Tests for the log_multiline.py module.

Created on 02/09/2014

@author: u76345
'''

from __future__ import absolute_import
import unittest
import os
import logging
import subprocess
from eotools.utils import log_multiline


class TestLogMultiline(unittest.TestCase):

    """Unit tests for the log_multiline utility function."""

    MODULE = 'eotools.utils'
    SUITE = 'TestLogMultiline'

    OUTPUT_DIR = '.'  # dbutil.output_directory(MODULE, SUITE)
    EXPECTED_DIR = '.'  # dbutil.expected_directory(MODULE, SUITE)

    def setUp(self):
        """Set up a test logger."""

        self.logger = logging.getLogger('TestLogMultiline')
        self.logger.setLevel(logging.DEBUG)

        self.handler = None

    def test_single_line_str(self):
        """Test of logging a single line string."""

        logfile_name = 'single_line_str.log'
        output_path = os.path.join(self.OUTPUT_DIR, logfile_name)
        expected_path = os.path.join(self.EXPECTED_DIR, logfile_name)

        self.open_handler(output_path)

        line = 'This is a single line log message.'
        prefix = 'TEST: '
        log_multiline(self.logger.debug, line, prefix=prefix)

        self.close_handler()
        self.check_expected_file(output_path, expected_path)

    def test_single_line_list(self):
        """Test of logging a single line as a list."""

        logfile_name = 'single_line_list.log'
        output_path = os.path.join(self.OUTPUT_DIR, logfile_name)
        expected_path = os.path.join(self.EXPECTED_DIR, logfile_name)

        self.open_handler(output_path)

        line = ['This is a single line log message.']
        title = 'SINGLE LINE AS LIST'
        log_multiline(self.logger.debug, line, title=title)

        self.close_handler()
        self.check_expected_file(output_path, expected_path)

    def test_multi_line_str(self):
        """Test of logging a multi-line string."""

        logfile_name = 'multi_line_str.log'
        output_path = os.path.join(self.OUTPUT_DIR, logfile_name)
        expected_path = os.path.join(self.EXPECTED_DIR, logfile_name)

        self.open_handler(output_path)

        line = ('This is a multi-line log message.\n' +
                'line 2\n'
                )
        log_multiline(self.logger.debug, line)

        self.close_handler()
        self.check_expected_file(output_path, expected_path)

    def test_multi_line_list(self):
        """Test of logging a multi-line message as a list."""

        logfile_name = 'multi_line_list.log'
        output_path = os.path.join(self.OUTPUT_DIR, logfile_name)
        expected_path = os.path.join(self.EXPECTED_DIR, logfile_name)

        self.open_handler(output_path)

        title = 'MULTI-LINE AS LIST'
        prefix = 'TEST:'
        line = ['This is a multi-line log message.',
                'line 2',
                'line 3'
                ]
        log_multiline(self.logger.debug,
                      line,
                      prefix=prefix,
                      title=title
                      )

        self.close_handler()
        self.check_expected_file(output_path, expected_path)

    def test_multi_line_dict(self):
        """Test of logging a dictionary."""

        logfile_name = 'multi_line_dict.log'
        output_path = os.path.join(self.OUTPUT_DIR, logfile_name)
        expected_path = os.path.join(self.EXPECTED_DIR, logfile_name)

        self.open_handler(output_path)

        dictionary = {'first': 'first dict item',
                      'second': 'second dict item',
                      'third': 'third dict item'
                      }
        log_multiline(self.logger.debug, dictionary)

        self.close_handler()
        self.check_expected_file(output_path, expected_path)

    def check_expected_file(self, output_path, expected_path):
        """Check the expected file matches the output file.

        This skips the test if the expected file does not exist.
        """

        if not os.path.isfile(expected_path):
            self.skipTest("Expected log file not found: " + expected_path)
        else:
            try:
                subprocess.check_output(['diff', output_path, expected_path])
            except subprocess.CalledProcessError as err:
                self.fail("Log file does not match expected result:\n" +
                          err.output)

    def open_handler(self, output_path):
        """Set up a file handler to the output path."""

        self.handler = logging.FileHandler(output_path, mode='w')
        self.logger.addHandler(self.handler)

    def close_handler(self):
        """Flush, remove, and close the handler."""

        self.handler.flush()
        self.logger.removeHandler(self.handler)
        self.handler.close()
        self.handler = None


def the_suite():
    """Returns a test suite of all the tests in this module."""

    test_classes = [
        TestLogMultiline
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
