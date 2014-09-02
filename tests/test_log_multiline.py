#!/usr/bin/env python

#===============================================================================
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
#===============================================================================

'''
Tests for the log_multiline.py module.

Created on 02/09/2014

@author: u76345
'''

import unittest
import os
import logging
import subprocess
from utils import log_multiline

class TestLogMultiline(unittest.TestCase):
    """Unit tests for the log_multiline utility function."""

    MODULE = 'cube_util'
    SUITE = 'TestLogMultiline'

    OUTPUT_DIR = '.' # dbutil.output_directory(MODULE, SUITE)
    EXPECTED_DIR = '.' #dbutil.expected_directory(MODULE, SUITE)

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

