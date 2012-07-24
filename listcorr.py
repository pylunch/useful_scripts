#!/usr/bin/env python
"""
This script will show the values of CRCORR and RPTCORR in the headers of given
fits files.

CRCORR = PERFORM for CR-SPLIT images, OMIT otherwise.
RPTCORR = PERFORM for REPEAT-OBS images, OMIT otherwise.

Usage: listcorr.py <fits files>
"""

import sys

import pyfits

def list_corr(fitsFiles):
  for fits in fitsFiles:
    head = pyfits.getheader(fits)
    
    crcorr = head['CRCORR']
    
    rptcorr = head['RPTCORR']
    
    print_corr(fits,crcorr,rptcorr)
    
def print_corr(fits,crcorr,rptcorr):
  print('')
  print(fits)
  print('CRCORR     ' + crcorr)
  print('RPTCORR    ' + rptcorr)

def usage():
  print('Usage: listcorr.py <fits files>')
  
if __name__ == '__main__':
  if len(sys.argv) < 2:
    usage()
    exit()
	
  list_corr(sys.argv[1:])
