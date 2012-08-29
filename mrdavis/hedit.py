#!/usr/bin/env python
"""
Add or modify a header value. Type hedit.py -h for help.

Author
------
Matt Davis (mrdavis@stsci.edu)

Examples
--------

Modify a single file:

> hedit.py jb1f98q1q_raw.fits EXPSTART 58000 -i
jb1f98q1q_raw.fits[0]: EXPSTART -> 58000

Modify multiple files:

> hedit.py *.fits FLATCORR PERFORM

Modify an extension header:

> hedit.py jb1f98q1q_raw.fits SOMEKEY SOMEVALUE --ext 1

"""

import argparse

import pyfits


def setval(fits, key, value, ext):
  print('{}[{}]: {} -> {}'.format(fits,ext,key,value))
  pyfits.setval(fits, key, value=value, ext=ext)


def parse_args():
  parser = argparse.ArgumentParser(description=
                                   'Add or modify a header value.')
  
  parser.add_argument('fits_files', nargs='+', type=str,
                      help='Name of fits files.')
                      
  parser.add_argument('keyword', help='Keyword to update.')
                      
  parser.add_argument('new_value', help='New value of keyword')
  
  parser.add_argument('-e', '--ext', type=int, default=0,
                      help='Extension number. Defaults to 0.')
                      
  parser.add_argument('-s', '--str', action='store_const', const=str,
                      dest='type', 
                      help='Value will be stored as string (default).')
                      
  parser.add_argument('-f', '--float', action='store_const', const=float,
                      dest='type', help='Value will be stored as float.')
                      
  parser.add_argument('-i', '--int', action='store_const', const=int,
                      dest='type', help='Value will be stored as integer.')
                      
  parser.add_argument('-b', '--bool', action='store_const', const=True,
                      dest='type', help='Value will be stored as boolean.')
  
  return parser.parse_args()


def main():
  args = parse_args()
  
  if args.type is not None:
    value_type = args.type
  else:
    # if nothing specified, default to string
    value_type = str
  
  # convert args.new_value to value_type
  if value_type is True:
    # boolean type
    if args.new_value == 'True':
      new_value = True
    elif args.new_value == 'False':
      new_value = False
    else:
      raise ValueError("Boolean values must be either 'True' or 'False'.")
  else:
    new_value = value_type(args.new_value)
  
  for fits_file in args.fits_files:
    setval(fits_file, args.keyword, new_value, args.ext)
  

if __name__ == '__main__':
  raise SystemExit(main())
