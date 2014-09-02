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
import os
import logging
import unicodedata
import re
from pprint import pformat

logger = logging.getLogger('root.' + __name__)


def log_multiline(log_function, log_text, title=None, prefix=''):
    """Function to log multi-line text
    """
    logger.debug('log_multiline(%s, %s, %s, %s) called', log_function, repr(log_text), repr(title), repr(prefix))

    if isinstance(log_text, str):
        logger.debug('log_text is type str')
        log_list = log_text.splitlines()
    elif isinstance(log_text, list) and isinstance(log_text[0], str):
        logger.debug('log_text is type list with first element of type text')
        log_list = log_text
    else:
        logger.debug('log_text is type ' + type(log_text).__name__)
        log_list = pformat(log_text).splitlines()

    log_function(prefix + '=' * 80)
    if title:
        log_function(prefix + title)
        log_function(prefix + '-' * 80)

    for line in log_list:
        log_function(prefix + line)

    log_function(prefix + '=' * 80)


def unicode_to_ascii(instring):
    """Convert unicode to char string if required and strip any leading/trailing whitespaces
    ToDO: Investigate whether we can just change the encoding of the DOM tree
    """
    result = instring
    if isinstance(result, unicode):
        result = unicodedata.normalize('NFKD', result).encode('ascii', 'ignore').strip(""" "'\n\t""")
    return result


def find_files(root_dir, filename_pattern='.*', case_insensitive=True):
    """
    List files matching a specified pattern (regex) anywhere under a root directory

    :param root_dir:
        Root directory to search within.

    :param filename_pattern:
        RegEx string for finding files.

    :param case_insensitive:
        Flag specifying whether name matching should be case insensitive.

    :return:
        List containing absolute pathnames of found files or empty list if none found.
    """
    if case_insensitive:
        file_regex = re.compile(filename_pattern, re.IGNORECASE)
    else:
        file_regex = re.compile(filename_pattern)

    filename_list = []

    for root, _dirs, files in os.walk(root_dir):
        for file_path in sorted(files):
            file_path = os.path.abspath(os.path.join(root, file_path))
            m = re.search(file_regex, file_path)
            if m:
                filename_list.append(file_path)

    return filename_list
