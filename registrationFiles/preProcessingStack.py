
import os, sys 
from ij import IJ
from ij.io import FileSaver

if len(sys.argv)<2:
	print "Usage: ./fiji-linux64 <inputStack>"

inputStack = sys.argv[1]

filename = os.path.splitext(inputStack)[0]
print filename
outputStack = filename + "_processed.tif"
im = IJ.openImage(inputStack)
IJ.run(im, "Median...", "radius=2 stack")
IJ.run(im, "Find Edges", "stack")
fs = FileSaver(im).saveAsTiff(outputStack)
