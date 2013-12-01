from pylut import *
import os
import timeit

def main():
	workingDirectory = os.path.dirname(os.path.realpath(__file__))

	lut = LUT.FromIdentity(32).ClampColor(Color(0,0,.3), Color(0,0,.7))
	lut *= .3

	lut2 = lut.CombineWithLUT(LUT.FromIdentity(lut.LatticeSize()))

	print lut.ColorAtLatticePoint(1,1,1)
	print lut2.ColorAtInterpolatedLatticePoint(1.1,.2,5.5)

	print lut.ColorFromColor(Color(.4,.4,.3))
	print lut.ColorFromColor(Color.FromRGBInteger(500,1022,40, bitdepth = 10))

	lut.ToNuke3DLFile(workingDirectory+"/test.cube")

main()