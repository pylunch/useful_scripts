#!/usr/bin/env python
"""
  This script will show the information in any *_asn.fits files in the current
  directory. _asn.fits files may also be specified as arguments to this script.
  """

import sys
import glob

import pyfits

def globasns():
  return glob.glob('*_asn.fits')

def listasns(asns):
  for asn in asns:
    listasn(asn)

def listasn(asn):
  print('')
  print(asn)
  print('File'.ljust(16) + 'Type'.ljust(16) + 'Present')
      
  a = pyfits.open(asn)
      
  for line in a[1].data:
    out = line[0].ljust(16) + line[1].ljust(16) + str(line[2])
    print(out)

if __name__ == '__main__':
  if len(sys.argv) == 1:
    asns = globasns()
    listasns(asns)
  else:
    listasns(sys.argv[1:])
