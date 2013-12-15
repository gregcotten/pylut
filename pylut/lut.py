from color        import Color
from reverser     import LUTReverser
from resizer      import LUTResizer
from plotter      import LUTPlotter
from combiner     import LUTCombiner

from formatters.LUTFormatterCube import LUTFormatterCube
from formatters.LUTFormatterLustre3DL import LUTFormatterLustre3DL
from formatters.LUTFormatterNuke3DL import LUTFormatterNuke3DL

class LUT:
	"""
	A class that represents a 3D LUT with a 3D numpy array. The idea is that the modifications are non-volatile, meaning that every modification method returns a new LUT object.
	"""
	def __init__(self, lattice, name = "Untitled LUT"):
		self.lattice = lattice
		"""
		Numpy 3D array representing the 3D LUT.
		"""

		self.cubeSize = self.lattice.shape[0]
		"""
		LUT is of size (cubeSize, cubeSize, cubeSize) and index positions are from 0 to cubeSize-1
		"""

		self.name = str(name)
		"""
		Every LUT has a name!
		"""

	# Transformers

	def Reverse(self, progress = False):
		"""
		Returns a new LUT that represents the reverse of this LUT. Warning: This can take a long time depending on if the input/output is a bijection.
		"""
		return LUTReverser(self.lut).Reverse(progress)

	def Resize(self, newCubeSize):
		"""
		Returns a new lut with the lattice resized to newCubeSize.
		"""
		return LUTResizer(self.lut).Resize(newCubeSize)

	def Combine(self, otherLUT):
		"""
		Returns a new lut combining self with otherLUT.
		"""
		return LUTCombiner(self.lut).Combine(otherLUT)

	def ClampColor(self, min, max):
		"""
		Returns a new RGB clamped LUT.
		"""
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					newLattice[x, y, z] = self.ColorAtLatticePoint(x, y, z).ClampColor(min, max)
		return LUT(newLattice)

	def ColorFromColor(self, color):
		"""
		Returns what a color value should be transformed to when piped through the LUT.
		"""
		color = color.Clamped01()
		cubeSize = self.cubeSize
		return self.ColorAtInterpolatedLatticePoint(color.r * (cubeSize-1), color.g * (cubeSize-1), color.b * (cubeSize-1))

	#integer input from 0 to cubeSize-1
	def ColorAtLatticePoint(self, redPoint, greenPoint, bluePoint):
		"""
		Returns a color at a specified lattice point - this value is pulled from the actual LUT file and is not interpolated.
		"""
		cubeSize = self.cubeSize
		if redPoint > cubeSize-1 or greenPoint > cubeSize-1 or bluePoint > cubeSize-1:
			raise NameError("Point Out of Bounds: (" + str(redPoint) + ", " + str(greenPoint) + ", " + str(bluePoint) + ")")

		return self.lattice[redPoint, greenPoint, bluePoint]

	#float input from 0 to cubeSize-1
	def ColorAtInterpolatedLatticePoint(self, redPoint, greenPoint, bluePoint):
		"""
		Gets the interpolated color at an interpolated lattice point.
		"""
		cubeSize = self.cubeSize

		if 0 < redPoint > cubeSize-1 or 0 < greenPoint > cubeSize-1 or 0 < bluePoint > cubeSize-1:
			raise NameError("Point Out of Bounds")

		lowerRedPoint = Clamp(int(math.floor(redPoint)), 0, cubeSize-1)
		upperRedPoint = Clamp(lowerRedPoint + 1, 0, cubeSize-1)

		lowerGreenPoint = Clamp(int(math.floor(greenPoint)), 0, cubeSize-1)
		upperGreenPoint = Clamp(lowerGreenPoint + 1, 0, cubeSize-1)

		lowerBluePoint = Clamp(int(math.floor(bluePoint)), 0, cubeSize-1)
		upperBluePoint = Clamp(lowerBluePoint + 1, 0, cubeSize-1)

		C000 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, lowerBluePoint)
		C010 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, upperBluePoint)
		C100 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, lowerBluePoint)
		C001 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, lowerBluePoint)
		C110 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, upperBluePoint)
		C111 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, upperBluePoint)
		C101 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, lowerBluePoint)
		C011 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, upperBluePoint)

		C00  = LerpColor(C000, C100, 1.0 - (upperRedPoint - redPoint))
		C10  = LerpColor(C010, C110, 1.0 - (upperRedPoint - redPoint))
		C01  = LerpColor(C001, C101, 1.0 - (upperRedPoint - redPoint))
		C11  = LerpColor(C011, C111, 1.0 - (upperRedPoint - redPoint))

		C1 = LerpColor(C01, C11, 1.0 - (upperBluePoint - bluePoint))
		C0 = LerpColor(C00, C10, 1.0 - (upperBluePoint - bluePoint))

		return LerpColor(C0, C1, 1.0 - (upperGreenPoint - greenPoint))

	@staticmethod
	def FromIdentity(cubeSize):
		"""
		Creates an indentity LUT of specified size.
		"""
		identityLattice = EmptyLatticeOfSize(cubeSize)
		indices01 = Indices01(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					identityLattice[r, g, b] = Color(indices01[r], indices01[g], indices01[b])
		return LUT(identityLattice, name = "Identity"+str(cubeSize))


	def AddColorToEachPoint(self, color):
		"""
		Add a Color value to every lattice point on the cube.
		"""
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] + color
		return LUT(newLattice)

	def SubtractColorFromEachPoint(self, color):
		"""
		Subtract a Color value to every lattice point on the cube.
		"""
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] - color
		return LUT(newLattice)

	def MultiplyEachPoint(self, color):
		"""
		Multiply by a Color value or float for every lattice point on the cube.
		"""
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] * color
		return LUT(newLattice)


	def __add__(self, other):
		if self.cubeSize is not other.cubeSize:
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice + other.lattice)

	def __sub__(self, other):
		if self.cubeSize is not other.cubeSize:
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice - other.lattice)

	def __mul__(self, other):
		className = other.__class__.__name__
		if "Color" in className or "float" in className or "int" in className:
			return self.MultiplyEachPoint(other)

		if self.cubeSize is not other.cubeSize:
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice * other.lattice)

	def __rmul__(self, other):
		return self.__mul__(other)

	def __eq__(self, lut):
		if isinstance(lut, LUT):
			return (self.lattice == lut.lattice).all()
		return NotImplemented

	def __ne__(self, lut):
		result = self.__eq__(lut)
		if result is NotImplemented:
			return result
		return not result

	def Plot(self):
		LUTPlotter.Plot(self)

	def ToFile(toType, path):
		if os.path.isfile(path) and not overwrite:
			exit("File already exists!")
		if toType in "L3DL":
			LUTFormatterLustre3DL.ToFile(self, path)
		elif toType in "N3DL":
			LUTFormatterNuke3DL.ToFile(self, path)
		elif toType in "RCUBE":
			LUTFormatterCube.ToFile(self, path)

	@staticmethod
	def FromFile(lutFilePath):
		lut = None
		filetype = None

		extension = os.path.splitext(lutFilePath)[1].lower()

		if ".3dl" in extension:
			try:
				lut = LUTFormatterLustre3DL.FromFile(lutFilePath)
				return lut, "L3DL"
			except Exception as e:
				pass
			try:
				lut = LUTFormatterNuke3DL.FromFile(lutFilePath)
				return lut, "N3DL"
			except Exception as e:
				pass
		elif ".cube" in extension:
			try:
				lut = LUTFormatterCube.FromFile(lutFilePath)
				return lut, "RCUBE"
			except Exception as e:
				pass

		return None, None


