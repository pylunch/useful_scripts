#!/usr/bin/env python
"""
Add or modify a header value. Type hedit -h for help.

Author
------
Matt Davis (mrdavis@stsci.edu)

Examples
--------

Modify a single file:

> hedit jb1f98q1q_raw.fits EXPSTART 58000 -i
jb1f98q1q_raw.fits[0]: EXPSTART -> 58000

Modify multiple files:

> hedit *.fits FLATCORR PERFORM

Modify an extension header:

> hedit jb1f98q1q_raw.fits SOMEKEY SOMEVALUE --ext 1

"""

import optparse

import pyfits


def setval(fits, key, value, ext):
  print('%s[%i]: %s -> %s' % (fits, ext, key, str(value)))
  pyfits.setval(fits, key, value=value, ext=ext)


def parse_args():
  usage = '%prog [options] fits_files keyword new_value'

  parser = optparse.OptionParser(usage = usage,
                                 description= 'Add or modify a header value.')
  
  parser.add_option('-e', '--ext', type='int', default=0,
                      help='Extension number. Defaults to 0.')
                      
  parser.add_option('-s', '--str', action='store_const', const=str,
                      dest='type', 
                      help='Value will be stored as string (default).')
                      
  parser.add_option('-f', '--float', action='store_const', const=float,
                      dest='type', help='Value will be stored as float.')
                      
  parser.add_option('-i', '--int', action='store_const', const=int,
                      dest='type', help='Value will be stored as integer.')
                      
  parser.add_option('-b', '--bool', action='store_const', const=True,
                      dest='type', help='Value will be stored as boolean.')
  
  options, args = parser.parse_args()
  
  if len(args) < 3:
    raise SystemExit(parser.print_help())
  
  fits_files = args[:-2]
  
  keyword = args[-2]
  
  new_value = args[-1]
  
  return fits_files, keyword, new_value, options


def main():
  fits_files, keyword, new_value, opts = parse_args()
  
  if opts.type is not None:
    value_type = opts.type
  else:
    # if nothing specified, default to string
    value_type = str
  
  # convert args.new_value to value_type
  if value_type is True:
    # boolean type
    if new_value == 'True':
      new_value = True
    elif new_value == 'False':
      new_value = False
    else:
      raise ValueError("Boolean values must be either 'True' or 'False'.")
  else:
    new_value = value_type(new_value)
  
  for fits_file in fits_files:
    setval(fits_file, keyword, new_value, opts.ext)
  

if __name__ == '__main__':
  raise SystemExit(main())
