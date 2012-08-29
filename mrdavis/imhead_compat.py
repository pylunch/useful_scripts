#!/usr/bin/env python
"""
Print a FITS header or keyword. Type imhead -h for help.

Author
------
Matt Davis (mrdavis@stsci.edu)

Examples
--------

Print the full primary header:

imhead jb1f98q1q_raw.fits

Print an extension header:

imhead -e 1 jb1f98q1q_raw.fits

Print only specified keywords:

imhead jb1f98q1q_raw.fits -k expstart -k expend

"""

import optparse

import pyfits


def print_header(fits, ext=0, keys=None):
  head = pyfits.getheader(fits, ext=ext).ascard
  
  if keys is None:
    print head
  else:
    for key in keys:
      print head[key]


def parse_args():
  usage = '%prog [options] fits_files'

  parser = optparse.OptionParser(usage=usage,
                                 description= 'Print a FITS header or keyword.')
                      
  parser.add_option('-e', '--ext', type='int', default=0,
                    help='Extension number. Defaults to 0.')
                      
  parser.add_option('-k', '--key', type='string', action='append',
                    help='Keyword to print.')
  
  opts, fits_files = parser.parse_args()
  
  if len(fits_files) < 1:
    raise SystemExit(parser.print_help())
    
  return fits_files, opts


def main():
  fits_files, opts = parse_args()
  
  for fits_file in fits_files:
    print_header(fits_file, opts.ext, opts.key)


if __name__ == '__main__':
  raise SystemExit(main())
