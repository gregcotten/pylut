from pylut import LUT
import os
import timeit

def main():
	workingDirectory = os.path.dirname(os.path.realpath(__file__))

	lut = LUT.FromIdentity(32).ClampRed(0,.5)
	lut *= .3

	lut2 = lut.CombineWithLUT(LUT.FromIdentity(lut.LatticeSize()))

	print lut.ColorAtLatticePoint(1,1,1)
	print lut2.ColorAtInterpolatedLatticePoint(1.1,.2,5.5)

	print lut.ColorAtRGB01(.5,.5,.5)
	print lut2.ColorAtRGBInt(1023, 90, 55, bitdepth = 10)

	lut.ToNuke3DLFile(workingDirectory+"/test.cube")

main()