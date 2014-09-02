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

"""
Provides utilities for logging and meta programming to DatasetDrivers.
"""

import threading, os
from functools import wraps
from inspect import getcallargs

RUNNING_SPHINX = os.environ.has_key('RUNNING_SPHINX_BUILD')

class Singleton(type):
    """
    Metaclass for Singletons.

    We could also keep the singletons in a dictionary in this class with keys of type
    class. I prefer, however, to keep them in the actual class.

    """
    def __new__(cls, name, bases, dct):
        dct['_instance_for_singleton_ssfusousoifusos'] = None
        dct['_lock_for_singleton_ssfusousoifusos'] = threading.Lock()
        return super(Singleton, cls).__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        if not cls._instance_for_singleton_ssfusousoifusos:
            with cls._lock_for_singleton_ssfusousoifusos:
                if not cls._instance_for_singleton_ssfusousoifusos:
                    cls._instance_for_singleton_ssfusousoifusos = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance_for_singleton_ssfusousoifusos





def create_arg_string(func, *args, **kwargs):
    """
    Constructs a string of the arguments passed to a function on a given invocation.

    :param func: The function for which the string is to be constructed.

    :param args: The positional arguments passed in the call to ``func``.

    :param kwargs: The keyword arguments passed in the call to ``func``.

    """
    return ',\n\t'.join(['='.join([str(y) for y in item]) for item in getcallargs(func, *args, **kwargs).iteritems()])





def print_call(logger):
    """
    Decorator which prints the call to a function, including all the arguments passed.

    :param func: The function to be decorated.

    :param logger: Callable which will be passed the string representation of the function call. Then no
        logging is performed (the decorated is simply returned.

    """

    def wrap(func):
        if RUNNING_SPHINX or not logger:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_str = create_arg_string(func, *args, **kwargs)
            logger('\ncalling %s.%s(\n\t%s\n)\n' % (func.__module__, func.__name__, arg_str))
            res = func(*args, **kwargs)
            logger("SUCCESS!")
            return res

        return wrapper

    return wrap
