#!/usr/bin/env python
"""
Print a FITS header or keyword. Type imhead.py -h for help.

Author
------
Matt Davis (mrdavis@stsci.edu)

Examples
--------

Print a header:

imhead.py jb1f98q1q_raw.fits

Print an extension header:

imhead.py -e 1 jb1f98q1q_raw.fits

Print only specified keywords:

imhead.py jb1f98q1q_raw.fits -k expstart -k expend

"""

import argparse

import pyfits


def print_header(fits, ext=0, keys=None):
  head = pyfits.getheader(fits, ext=ext).ascard

  if not keys:
    print head
  else:
    for key in keys:
      print head[key]


def parse_args():
  parser = argparse.ArgumentParser(description=
                                   'Print a FITS header or keyword.')

  parser.add_argument('fits_files', nargs='+', type=str,
                      help='Name of fits files.')

  parser.add_argument('-e', '--ext', type=int, default=0,
                      help='Extension number. Defaults to 0.')

  parser.add_argument('-k', '--key', type=str, action='append',
                      help='Keyword to print.')

  return parser.parse_args()


def main():
  args = parse_args()

  for fits_file in args.fits_files:
    print_header(fits_file, args.ext, args.key)


if __name__ == '__main__':
  raise SystemExit(main())
