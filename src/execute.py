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

"""
Provides the function :py:func:`execute`. This needs to be defined in a separate file to avoid
circular imports.
"""
from __future__ import absolute_import
from __future__ import print_function
import os
import subprocess
import time
import pdb
import pprint


def execute(command_string=None, shell=True, cwd=None, env=None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=None, close_fds=False, bufsize=-1,
            debug=False):
    """
    Executes a command as a subprocess.

    This function is a thin wrapper around :py:func:`subprocess.Popen` that gathers some extra information
    on the subprocess's execution context and status.  All arguments except 'debug' are passed through
    to :py:func:`subprocess.Popen` as-is.

    :param command_string:
        Commands to be executed.

    :param shell:
        Execute via the shell

    :param cwd:
        Working directory for the subprocess

    :param env:
        Environment for the subprocess

    :param stdout:
        stdout for the subprocess

    :param stderr:
        stdout for the subprocess

    :param close_fds:
        close open file descriptors before execution

    :param bufsize:
        buffer size

    :param debug:
        debug flag

    :return:
        Dictionary containing command, execution context and status:
            { 'command': <str>,
            'returncode': <int>,
            'pid': <int>,
            'stdout': <stdout text>,
            'stderr': <stderr text>,
            'caller_ed': <caller working directory>,
            'env': <execution environment>,}

    :seealso:
        :py:func:`subprocess.Popen`
    """

    assert command_string
    parent_wd = os.getcwd()

    p = subprocess.Popen(
        command_string,
        shell=shell,
        cwd=cwd,
        env=env,
        stdout=stdout,
        stderr=stderr,
        bufsize=bufsize,
        close_fds=close_fds,
        preexec_fn=preexec_fn,
    )
    start_time = time.time()
    out, err = p.communicate()
    result = {
        'command': command_string,
        'returncode': p.returncode,
        'pid': p.pid,
        'stdout': out,
        'stderr': err,
        'parent_wd': parent_wd,
        'cwd': cwd,
        'env': env,
        'elapsed_time': time.time() - start_time,
    }

    if debug:
        print('\n*** DEBUG ***')
        print('sub_process.execute')
        pprint.pprint(result)
        pdb.set_trace()

    return result

    # if debug and p.returncode:
    #    pdb.set_trace()
