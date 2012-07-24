#!/usr/bin/env python
"""
NOTE: just use fitsdiff.

This script compares two fits files and gives some information about whether it
thinks they are the same, in the sense that their headers and data appear to be
the same.

Usage: compfits.py <fits file 1> <fits file 2>

"""

import sys

import numpy as np

import pyfits

# some header values we can't expect to be the same (e.g. time lost modified)
# so let up a global list of those values here and make sure they're ignored
# in CompareFits.compare_header_values()
IGNORE_HEADER_VALUES = ['IRAF-TLM','DATE']

class FitsError(Exception):
  """
  Base class of exceptions for comparing fits files.

  """
  pass

class FitsLengthError(FitsError):
  """
  Exception raised when fits files do not have the same number of extensions.

  Attributes:
    len_fits1 -- number of extensions in first fits file
    len_fits2 -- number of extensions in second fits file
    message -- may contain a message describing the error

  """
  def __init__(self,len_fits1,len_fits2,msg=''):
    self.len_fits1 = len_fits1
    self.len_fits2 = len_fits2
    self.msg = msg

class FitsExtensionNamesError(FitsError):
  """
  Exception raised when fits files not have the same extention names in the
  same order.

  Attributes:
    names1 -- list of extension names from first fits file
    names2 -- list of extension names from second fits file
    msg -- may contain a message describing the error

  """
  def __init__(self,names1,names2,msg=''):
    self.names1 = names1
    self.names2 = names2
    self.msg = msg

class FitsSizeError(FitsError):
  """
  Exception raised when fits file extensions do not have the same size as
  reported by the .size() and/or .filebytes() methods.

  Attributes:
    size1 -- list of extension .size() values for first fits file
    size2 -- list of extension .size() values for second fits file
    filebytes1 -- list of extension .filebytes() values for first fits file
    filebytes2 -- list of extension .filebytes() values for second fits file
    msg -- may contain a message describing the error

  """
  def __init__(self,size1,size2,filebytes1,filebytes2,msg=''):
    self.size1 = size1
    self.size2 = size2
    self.filebytes1 = filebytes1
    self.filebytes2 = filebytes2
    self.msg = msg

class FitsHeaderKeyError(FitsError):
  """
  Exception raised when fits file headers have different keys.

  Attributes:
    header1 -- first fits file header (pyfits.PrimaryHDU object)
    header2 -- second fits file header (pyfits.PrimaryHDU object)
    header1_extra_keys -- list of header keys in first fits but not second
    header2_extra_keys -- list of header keys in second fits but not first
    ext_num -- fits file extension number for this error
    msg -- may contain a message describing the error

  """
  def __init__(self,header1,header2,
               header1_extra_keys,header2_extra_keys,
               ext_num,msg=''):
    self.header1 = header1
    self.header2 = header2
    self.header1_extra_keys = header1_extra_keys
    self.header2_extra_keys = header2_extra_keys
    self.ext_num = ext_num
    self.msg = msg

class FitsHeaderValueError(FitsError):
  """
  Exception raised when fits file headers have different values.

  Attributes:
    header1 -- first fits file header (pyfits.PrimaryHDU object)
    header2 -- second fits file header (pyfits.PrimaryHDU object)
    diff_keys -- list of header keys for which the values differ
    ext_num -- fits file extension number for this error
    msg -- may contain a message describing the error

  """
  def __init__(self,header1,header2,diff_keys,ext_num,msg=''):
    self.header1 = header1
    self.header2 = header2
    self.diff_keys = diff_keys
    self.ext_num = ext_num
    self.msg = msg

class FitsDataError(FitsError):
  """
  Exception raised when fits extension data are not the same shape or are unequal.

  Attributes:
    data1 -- data array from first fits file
    data2 -- data array from second fits file
    ext_num -- fits extension number for this error
    msg -- may contain a message describing the error

  """
  def __init__(self,data1,data2,ext_num,msg=''):
    self.data1 = data1
    self.data2 = data2
    self.ext_num = ext_num
    self.msg = msg


class CompareFits:
  def __init__(self,fits1,fits2):
    self.fits_file1 = fits1
    self.fits_file2 = fits2

    self.fits1 = pyfits.open(fits1)
    self.fits2 = pyfits.open(fits2)

  def compare_length(self):
    """
    Compare the number of extensions in the fits files using len(fits).
    Raises FitsLengthError when fiels do not have the same number of extensions.

    """
    same_length = False

    len_fits1 = len(self.fits1)
    len_fits2 = len(self.fits2)

    if len_fits1 == len_fits2:
      same_length = True
    elif len_fits1 > len_fits2:
      msg = 'Fits1 has more extensions than Fits2.'
      raise FitsLengthError(len_fits1,len_fits2,msg)
    elif len_fits1 < len_fits2:
      msg = 'Fits2 has more extensions than Fits1.'
      raise FitsLengthError(len_fits1,len_fits2,msg)

    return same_length

  def compare_names(self):
    """
    Compare the names of the fits file extensions. Raises FitsExtensionNamesError
    when the files do not have the same extension names in the same order.

    """
    same_names = False

    names1 = [x.name for x in self.fits1]
    names2 = [x.name for x in self.fits2]

    if names1 == names2:
      same_names = True
    else:
      msg = 'Fits file extensions do not have the same names.\n'
      msg += '\tFits1 names: ' + repr(names1) + '\n'
      msg += '\tFits2 names: ' + repr(names2) + '\n'
      raise FitsExtensionNamesError(names1,names2,msg)

    return same_names

  def compare_size(self):
    """
    Verify that the .size() and .filebytes() methods return matching values
    for each extension of the fits files. Raises FitsSizeError if either or
    both sets of sizes do not match.

    """
    same_size = False

    size1 = [x.size() for x in self.fits1]
    size2 = [x.size() for x in self.fits2]

    filebytes1 = [x.filebytes() for x in self.fits1]
    filebytes2 = [x.filebytes() for x in self.fits2]

    if (size1 == size2) and (filebytes1 == filebytes2):
      same_size = True
    elif (size1 != size2) and (filebytes1 != filebytes2):
      msg = 'Fits file extensions do not have the same .size() or \n'
      msg += '.filebytes() sizes.\n'
      msg += '.size() sizes:\n'
      msg += '\tFits1 sizes: ' + repr(size1) + '\n'
      msg += '\tFits2 sizes: ' + repr(size2) + '\n'
      msg += '.filebytes() sizes:\n'
      msg += '\tFits1 filebytes: ' + repr(filebytes1) + '\n'
      msg += '\tFits2 filebytes: ' + repr(filebytes2) + '\n'
      raise FitsSizeError(size1,size2,filebytes1,filebytes2,msg)
    elif (size1 == size2):
      msg = 'Fits file extensions do not have the same .size() values.\n'
      msg += '\tFits1 sizes: ' + repr(size1) + '\n'
      msg += '\tFits2 sizes: ' + repr(size2) + '\n'
      raise FitsSizeError(size1,size2,filebytes1,filebytes2,msg)
    elif (filebytes1 == filebytes2):
      msg = 'Fits file extensions do not have the same .filebytes() values.\n'
      msg += '\tFits1 filebytes: ' + repr(filebytes1) + '\n'
      msg += '\tFits2 filebytes: ' + repr(filebytes2) + '\n'
      raise FitsSizeError(size1,size2,filebytes1,filebytes2,msg)

    return same_size

  def compare_header_keys(self,ext_num):
    """
    Verify that the fits files have the same header keys. Raises
    FitsHeaderKeyError if the headers have different keys.

    Input:
      ext_num -- extension number (zero based) for which to compare heaer keys

    """
    same_header_keys = False

    header_keys1 = sorted(self.fits1[ext_num].header.keys())
    header_keys2 = sorted(self.fits2[ext_num].header.keys())

    if header_keys1 == header_keys2:
      same_header_keys = True
    else:
      header1_extra_keys = sorted(set(header_keys1).difference(set(header_keys2)))
      header2_extra_keys = sorted(set(header_keys2).difference(set(header_keys1)))
      msg = 'Fits files do not have the same header keys for extension ' + \
            str(ext_num) + '.\n'
      msg += 'Header keys in Fits1 but not Fits2:\n'
      msg += '\t' + repr(header1_extra_keys) + '\n'
      msg += 'Header keys in Fits2 but not Fits1:\n'
      msg += '\t' + repr(header2_extra_keys) + '\n'
      raise FitsHeaderKeyError(self.fits1[ext_num].header,self.fits2[ext_num].header,
                               header1_extra_keys,header2_extra_keys,ext_num,msg)

    return same_header_keys

  def compare_header_values(self,ext_num):
    """
    Veryify that fits files have the same header values, assuming they have the
    same header keys. Raises FitsHeaderValueError if the headers have different
    values.

    Input:
      ext_num -- extension number (zero based) for which to compare header values

    """
    same_header_values = False

    header1 = self.fits1[ext_num].header
    header2 = self.fits2[ext_num].header

    diff_keys = []

    for key in header1.keys():
      if (header1[key] != header2[key]) and (key not in IGNORE_HEADER_VALUES):
        diff_keys.append(key)

    if len(diff_keys) == 0:
      same_header_values = True
    else:
      msg = 'Fits files have different values for some keys for extension '
      msg += 'number ' + str(ext_num) + '.\n'
      msg += 'Header keys with different values:\n'
      msg += '\t' + repr(diff_keys) + '\n'
      raise FitsHeaderValueError(header1,header2,diff_keys,ext_num,msg)

    return same_header_values

  def compare_header_num(self,ext_num):
    """
    Runs self.compare_header_keys() and self.compare_header_values() and returns
    True if both tests pass.

    Input:
      ext_num -- extension number (zero based) for which to compare headers

    """
    if (self.compare_header_keys(ext_num) is True) and \
       (self.compare_header_values(ext_num) is True):
      return True
    else:
      return False

  def compare_all_headers(self):
    """
    Runs self.compare_header_num() for all fits file extensions, assuming the
    fits files have the same number of extensions. Returns True if
    compare_header_num returns True for all extensions.

    """
    same_headers = True

    for i in range(len(self.fits1)):
      if self.compare_header_num(i) is not True:
        same_headers = False
        break

    return same_headers

  def compare_data_array(self,ext_num):
    """
    Compare data ararys for a fits extension. Checks whether they are the same
    shape and contain the same values.

    Input:
      ext_num -- extension number (zero based) for which to compare data

    """
    same_data = False

    data1 = self.fits1[ext_num].data
    data2 = self.fits2[ext_num].data

    if data1.shape == data2.shape:
      data_comp = (data1 == data2)
    else:
      msg = 'Data arrays for fits extension ' + str(ext_num) + ' do not have\n'
      msg += 'matching shapes.\n'
      msg += 'Fits1 shape: ' + repr(data1.shape) + '\n'
      msg += 'Fits2 shape: ' + repr(data2.shape) + '\n'
      raise FitsDataError(data1,data2,ext_num,msg)

    if bool(data_comp.all()) is True:
      same_data = True
    else:
      msg = 'Data arrays for fits extension ' + str(ext_num) + ' are not equal.\n'
      raise FitsDataError(data1,data2,ext_num,msg)

    return same_data

  def compare_data(self):
    """
    Runs self.compare_data_array for all data arrays in the fits files, assuming
    the files contain the same number of extensions. Returns True if
    compar_data_array returns True for all data extensions.

    """
    same_data = True

    # loop over all fits extensions but we only want to run compare_data_array
    # on the extensions that actually contain data arrays.
    for i in range(len(self.fits1)):
      if (type(self.fits1[i]) == pyfits.ImageHDU) and \
         (type(self.fits2[i]) == pyfits.ImageHDU) and \
         (type(self.fits1[i].data) == np.ndarray) and \
         (type(self.fits2[i].data) == np.ndarray):

        if self.compare_data_array(i) is not True:
          same_data = False
          break

    return same_data

  def close_fits(self):
    """
    Closes self.fits1 and self.fits2.

    """
    self.fits1.close()
    self.fits2.close()

  def run_all_comps(self):
    """
    Runs all comparisons in a logical order. Returns True if they all pass. If
    any exceptions are raised they are not handled.

    """
    same_length = self.compare_length()
    same_names = self.compare_names()
    same_size = self.compare_size()
    same_headers = self.compare_all_headers()
    same_data = self.compare_data()

    self.close_fits()

    same_fits = bool(np.bool_([same_length,same_names,same_size,
                               same_headers,same_data]).all())

    return same_fits

def comp_fits(fits1,fits2):
  comp = CompareFits(fits1,fits2)

  try:
    same_fits = comp.run_all_comps()
  except (FitsLengthError,
          FitsExtensionNamesError,
          FitsSizeError,
          FitsHeaderKeyError,
          FitsHeaderValueError,
          FitsDataError) as e:
    print(e.msg)
    raise
  except:
    raise
  else:
    if same_fits is True:
      print('All sameness tests passed for files: ')
      print('\t' + fits1 + '    ' + fits2)
    else:
      print('Some tests failed but did not raise exceptions,')
      print('you should check that out.')

def usage():
  print('Usage: compfits.py <fits file 1> <fits file 2>')

if __name__ == '__main__':
  if len(sys.argv) != 3:
    usage()
    exit()

  fits1 = sys.argv[1]
  fits2 = sys.argv[2]

  comp_fits(fits1,fits2)
