pylut
=====

Builds, modifies, visualizes, and converts 3D LUTs from popular .cube and .3dl formats. Source available at https://github.com/gregcotten/pylut.

Usage
-----

The idea is that the modifications to a LUT object are non-volatile, meaning that every modification method returns a new LUT object rather than changing the existing object. All sorts of great things can happen!

.. code:: python

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

CLI
---

There's also a CLI available.

Example:

::

    pylut some_lut.3dl --resize 17 --convert RCUBE

Contributing
------------

1. Fork it
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Commit your changes (``git commit -am 'Add some feature'``)
4. Push to the branch (``git push origin my-new-feature``)
5. Create new Pull Request