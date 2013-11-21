# pylut

Builds and modifies 3D LUTs.

## Installation

	sudo pip install pylut

## Usage

All sorts of great things can happen!

	from pylut import *
	lut = LUT.FromLustre3DLFile("/path/to/file.3dl")
	lut2 = LUT.FromLustre3DLFile("/path/to/file2.3dl")

	print lut.ColorAtLatticePoint(1,2,1)
	print lut.ColorAtInterpolatedLatticePoint(1.3,1.5,1.2)
	print lut.ColorAtRGB01(.002,.5,.2344)
	print lut.ColorAtRGBInt(14, 1000, 30, bitdepth = 10)

	lut3 = lut.CombineWithLUT(lut2)

	lut3 *= .5
	lut3 -= LUT.FromIdentity(lut3.LatticeSize())

	lut3 = lut3.ClampedRGB(.1,.7)

	lut3 = lut3.Resize(33)
	lut3.ToNuke3DLFile("/path/to/destination.3dl")


## The Future

1. No clue.


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
