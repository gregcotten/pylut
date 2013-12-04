#!/usr/bin/env python

"""pylut-cli

Usage:
  pylut-cli.py [-hvf] [-r=<size>] [-c=<convert>] [-n=<name>] [-o=<output_folder>] <file>
  pylut-cli.py --version

Options:
  -h --help                                     show this help message and exit
  --version                                     show version and exit
  -v --verbose                                  print status messages
  -f, --force                                   overwrite files if necessary
  -r <size>, --resize <size>                    rescale lut
  -c <convert>, --convert <convert>             convert to a different LUT format (L3DL, N3DL, RCUBE)
  -n <name>, --name <name>                         name to use for saved LUT
  -o <output_folder>, --output <output_folder>  set output folder [default: ./]

"""


try:
    from docopt import docopt
except ImportError:
    exit('This example requires docopt. Please run: \n    pip install docopt\n')

from pylut import *
import os

def LUTFromFile(lutFilePath):
  lut = None
  filetype = None

  if ".3dl" in os.path.splitext(lutFilePath)[1].lower():
    try:
      lut = LUT.FromLustre3DLFile(lutFilePath)
      filetype = "L3DL"
    except NameError:
      pass
    try:
      lut = LUT.FromNuke3DLFile(lutFilePath)
      filetype = "N3DL"
    except NameError:
      pass
  elif ".cube" in os.path.splitext(lutFilePath)[1].lower():
    try:
      lut = LUT.FromCubeFile(lutFilePath)
      filetype = "RCUBE"
    except NameError:
      pass
  
  if lut is None:
    raise NameError("File extension invalid.")

  return lut, filetype

def FullFilePath(outputFolder, name, extension):
  return outputFolder + "/" + name + extension

if __name__ == "__main__":
  arguments = docopt(__doc__, version='1.0')


  filePath = os.path.expanduser(arguments["<file>"])
  outputFolder = os.path.abspath(arguments["--output"])
  name = arguments["--name"]
  resizeSize = arguments["--resize"]
  convertType = arguments["--convert"]
  overwrite = arguments["--force"]

  if resizeSize is None and convertType is None:
    exit()

  if convertType is not None and convertType not in ("L3DL", "N3DL", "RCUBE"):
    raise NameError(str(convertType) + " is not a valid type to convert the LUT to.")

  if not os.path.isfile(filePath):
    raise NameError("Invalid file path.")


  lut, filetype = LUTFromFile(filePath)

  if resizeSize is not None:
    lut = lut.Resize(int(resizeSize))

  if name is None:
    name = lut.name
  else:
    name = os.path.splitext(name)[0]

  if convertType is None:
    toType = filetype
  else:
    toType = convertType

  if toType in "L3DL":
    if os.path.isfile(FullFilePath(outputFolder, name, ".3dl")) and not overwrite:
      exit("File already exists!")
    
    lut.ToLustre3DLFile(FullFilePath(outputFolder, name, ".3dl"))
  elif toType in "N3DL":
    if os.path.isfile(FullFilePath(outputFolder, name, ".3dl")) and not overwrite:
      exit("File already exists!")
    
    lut.ToNuke3DLFile(FullFilePath(outputFolder, name, ".3dl"))
  elif toType in "RCUBE":
    if os.path.isfile(FullFilePath(outputFolder, name, ".cube")) and not overwrite:
      exit("File already exists!")
    
    lut.ToCubeFile(FullFilePath(outputFolder, name, ".cube"))







  