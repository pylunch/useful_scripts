#!/usr/bin/env python
"""
Move input fits files to have form "_ref.fits".

Usage: mvref.py <input files>
"""

import os.path
import sys
import shutil

def mvref(files):
  for f in files:
    if os.path.exists(f):
      newf = f[:-5] + '_ref' + f[-5:]
      print('Moving file ' + f + ' to ' + newf)
      shutil.move(f,newf)
    else:
      print('File does not exist: ' + f)
      
def usage():
  print('mvref.py <input files>')
  
if __name__ == '__main__':
  
  if len(sys.argv) < 2:
    usage()
    exit()
    
  mvref(sys.argv[1:])
