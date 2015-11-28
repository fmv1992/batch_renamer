# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 21:41:03 2015

@author: monteiro

Description: renames all files (except pdfs) and folders allowing only ascii
letters, numbers and underlines.
For pdfs if the string '_-_' is present, preserve the first part of the string
as uppercase names and processes the rest.
"""
import os
import string
import unidecode
import re

und_dash_und = re.compile('\_\-\_')

def trimm_filename(x):
    """
    Processes file name allowing some non ascii characters present in
    allowed.
    """
    # general multi purpose decoding of invalid characters
    x_decoded = unidecode.unidecode(x)
    # translates string into alphanum and '-' , '_', '.' enabled chars
    x_decoded = re.sub('[^\-\_\.A-Za-z0-9]+', '_', x_decoded)
    # removes double underline occurences
    x_decoded = re.sub('\_+', '_', x_decoded)
    # substitutes every occurence of '.' except the last; .tar.gz DONT'T DO THAT
    #x_decoded = re.sub('\.(?=.*\.)', '', x_decoded)
    # splits filename and extension
    filename = re.match('.*?(?=\.)', x_decoded)
    extension = re.search('(?<=\.).+', x_decoded)
    # processes extension
    if extension:
        extension = extension.group(0).lower()
    # processes filename without extension
    if filename is None:
        filename = x_decoded
    else:
        filename = filename.group(0)
        # converts to lowercase
    filename = filename.lower()
        # don't allow last character to be special, neither the first
    filename = re.sub('[^a-zA-Z0-9]+$', '', filename)
    filename = re.sub('^[^a-zA-Z0-9]+', '', filename)
    if extension is None:
        new_string = filename
    else:
        new_string = filename + '.' + extension
    return new_string

def trimm_foldername(x):
    """Processes folder name allowing some non ascii characters."""
    # general multi purpose decoding of invalid characters
    x_decoded = unidecode.unidecode(x)
    # translates string into alphanum and '-' , '_', '.' enabled chars
    x_decoded = re.sub('[^\-\_\.A-Za-z0-9]', '_', x_decoded)
        # don't allow last character to be special, neither the first
    x_decoded = re.sub('[^a-zA-Z0-9]+$', '', x_decoded)
    x_decoded = re.sub('^[^a-zA-Z0-9]+', '', x_decoded)
    # removes double underline occurences
    x_decoded = re.sub('\_+', '_', x_decoded)
    new_string = x_decoded
    return new_string
    
    