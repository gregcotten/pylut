# pylut

A python module that builds, modifies, visualizes, and converts 3D LUTs from popular .cube and .3dl formats. The end goal for this module is to remove the obfuscation from proprietary LUT formats and provide a way to programmatically manipulate LUTs.

## Installation

	sudo pip install pylut

And to upgrade:

	sudo pip uninstall pylut
        sudo pip install pylut

## Documentation
	
Very mediocre docs viewable at: http://pythonhosted.org/pylut/

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

## Special Notes

In order to run
	
	lut.Plot()

You need to either be running OSX or have PyQt4 or PyGTK installed in order to visualize the cube.


## The Future

1. No clue.


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/gregcotten/pylut/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

