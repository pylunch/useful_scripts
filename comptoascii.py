#!/usr/bin/env python
"""
Convert a component throughput table with WAVELENGTH and THROUGHPUT columns
to an ASCII file with the same columns.

Not to be used with component tables that contain more than 2 columns.

"""

import os.path

import pyfits

def comp_to_ascii(comp_tab):
  base = os.path.basename(comp_tab)
  
  outname = os.path.splitext(base)[0] + '.txt'
  
  print('Saving data to {}'.format(outname))
  
  f = pyfits.open(comp_tab,'readonly')
  
  outfile = open(outname,'w')
  
  outfile.write('{:<20}{:<20}\n'.format('wavelength','throughput'))
  
  for row in f[1].data:
    outfile.write('{:<20}{:<20}\n'.format(row['wavelength'],row['throughput']))
    
  outfile.close()
  f.close()

def usage():
  print('Usage: comptoascii.py <component table name>')

if __name__ == '__main__':
  import sys
  
  if len(sys.argv) != 2:
    usage()
    exit()
    
  comp_to_ascii(sys.argv[1])
