# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 21:41:03 2015

@author: monteiro

Description: renames all files; simple as that
"""
import re
import os

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(x):
        return re.sub('\W', '', x, re.ASCII)

def primitive_name(x):
    if isinstance(x, str):
