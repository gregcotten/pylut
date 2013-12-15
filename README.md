# pylut

![pylut](http://www.gregcotten.com/files/plot.jpg)

A python module that builds, modifies, visualizes, and converts 3D LUTs from popular .cube and .3dl formats. The end goal for this module is to remove the obfuscation from proprietary LUT formats and provide a way to programmatically manipulate LUTs.

## Installation

	pip install pylut

And to upgrade:

	pip uninstall pylut
	pip install pylut

## Documentation

Very mediocre docs viewable at: http://pythonhosted.org/pylut/

## Usage

The idea is that the modifications to a LUT object are non-volatile, meaning that every modification method returns a new LUT object rather than changing the existing object. All sorts of great things can happen!

```python
from pylut import *

lut = LUT.FromFile("mylut.3dl")

# Query
print lut.ColorAtLatticePoint(1, 2, 1)
print lut.ColorAtInterpolatedLatticePoint(1.3, 1.5, 1.2)
print lut.ColorFromColor(Color(0.002, 0.5, 0.2344))
print lut.ColorFromColor(Color.FromRGBInteger(14, 1000, 30, bitdepth = 10))

# Combine
combinedLut = lut.CombineWithLUT(LUT.FromFile("otherlut.3dl"))

# Modify
lut *= .5
lut -= LUT.FromIdentity(lut.cubeSize)
lut = lut.ClampColor(Color(0, 0, 0.2), Color(0, 0, 0.4))

# Resize
resizedLut = lut.Resize(33)

# Save and Convert
lut.ToFile("CUBE", "mylut.cube")

```

#### Supported LUT Formats

- `.cube`
- `.3dl` from Autodesk Lustre
- `.3dl` from NUKE

## CLI

There's also a CLI available.

Example:

	pylut lut.3dl --resize 17 --convert RCUBE

This will resize the LUT to 17×17×17 and convert it from a `.3dl` to a `.cube` file.

## Special Notes

In order to run

```python
lut.Plot()
```

You need to either be running OSX or have PyQt4 or PyGTK installed in order to visualize the cube.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/gregcotten/pylut/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

