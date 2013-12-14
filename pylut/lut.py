from color import Color
from reverser import LUTReverser

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

	def Reverse(self, progress = false):
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

	
	def ToLustre3DLFile(self, fileOutPath, bitdepth = 12):
		cubeSize = self.cubeSize
		inputDepth = math.log(cubeSize-1, 2)

		if int(inputDepth) != inputDepth:
			raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

		lutFile = open(fileOutPath, 'w')

		lutFile.write("3DMESH\n")
		lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 10)]) + "\n")
		
		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

		lutFile.close()

	def ToCubeFile(self, cubeFileOutPath):
		cubeSize = self.cubeSize
		cubeFile = open(cubeFileOutPath, 'w')
		cubeFile.write("LUT_3D_SIZE " + str(cubeSize) + "\n")
		
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex / (cubeSize*cubeSize)

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()
			
			cubeFile.write( latticePointColor.FormattedAsFloat() )
			
			if(currentCubeIndex != cubeSize**3 - 1):
				cubeFile.write("\n")

		cubeFile.close()


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

	@staticmethod
	def FromLustre3DLFile(lutFilePath):
		lutFile = open(lutFilePath, 'rU')
		lutFileLines = lutFile.readlines()
		lutFile.close()

		meshLineIndex = 0
		cubeSize = -1

		for line in lutFileLines:
			if "Mesh" in line:
				inputDepth = int(line.split()[1])
				outputDepth = int(line.split()[2])
				cubeSize = 2**inputDepth + 1
				break
			meshLineIndex += 1

		if cubeSize == -1:
			raise NameError("Invalid .3dl file.")

		lattice = EmptyLatticeOfSize(cubeSize)
		currentCubeIndex = 0
		
		for line in lutFileLines[meshLineIndex+1:]:
			if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
				#valid cube line
				redValue = line.split()[0]
				greenValue = line.split()[1]
				blueValue = line.split()[2]

				redIndex = currentCubeIndex / (cubeSize*cubeSize)
				greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
				blueIndex = currentCubeIndex % cubeSize

				lattice[redIndex, greenIndex, blueIndex] = Color.FromRGBInteger(redValue, greenValue, blueValue, bitdepth = outputDepth)
				currentCubeIndex += 1

		return LUT(lattice, name = os.path.splitext(os.path.basename(lutFilePath))[0])


	@staticmethod
	def FromCubeFile(cubeFilePath):
		cubeFile = open(cubeFilePath, 'rU')
		cubeFileLines = cubeFile.readlines()
		cubeFile.close()

		cubeSizeLineIndex = 0
		cubeSize = -1

		for line in cubeFileLines:
			if "LUT_3D_SIZE" in line:
				cubeSize = int(line.split()[1])
				break
			cubeSizeLineIndex += 1
		if cubeSize == -1:
			raise NameError("Invalid .cube file.")

		lattice = EmptyLatticeOfSize(cubeSize)
		currentCubeIndex = 0
		for line in cubeFileLines[cubeSizeLineIndex+1:]:
			if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
				#valid cube line
				redValue = float(line.split()[0])
				greenValue = float(line.split()[1])
				blueValue = float(line.split()[2])

				redIndex = currentCubeIndex % cubeSize
				greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
				blueIndex = currentCubeIndex / (cubeSize*cubeSize)

				lattice[redIndex, greenIndex, blueIndex] = Color(redValue, greenValue, blueValue)
				currentCubeIndex += 1

		return LUT(lattice, name = os.path.splitext(os.path.basename(cubeFilePath))[0])

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
		"""
		Plot a LUT as a 3D RGB cube using matplotlib. Stolen from https://github.com/mikrosimage/ColorPipe-tools/tree/master/plotThatLut.
		"""
		
		try:
			import matplotlib
			# matplotlib : general plot
			from matplotlib.pyplot import title, figure
			# matplotlib : for 3D plot
			# mplot3d has to be imported for 3d projection
			import mpl_toolkits.mplot3d
			from matplotlib.colors import rgb2hex
		except ImportError:
			print "matplotlib not installed. Run: pip install matplotlib"
			return

		#for performance reasons lattice size must be 9 or less
		lut = None
		if self.cubeSize > 9:
			lut = self.Resize(9)
		else:
			lut = self


		# init vars
		cubeSize = lut.cubeSize
		input_range = xrange(0, cubeSize)
		max_value = cubeSize - 1.0
		red_values = []
		green_values = []
		blue_values = []
		colors = []
		# process color values
		for r in input_range:
			for g in input_range:
				for b in input_range:
					# get a value between [0..1]
					norm_r = r/max_value
					norm_g = g/max_value
					norm_b = b/max_value
					# apply correction
					res = lut.ColorFromColor(Color(norm_r, norm_g, norm_b))
					# append values
					red_values.append(res.r)
					green_values.append(res.g)
					blue_values.append(res.b)
					# append corresponding color
					colors.append(rgb2hex([norm_r, norm_g, norm_b]))
		# init plot
		fig = figure()
		fig.canvas.set_window_title('pylut Plotter')
		ax = fig.add_subplot(111, projection='3d')
		ax.set_xlabel('Red')
		ax.set_ylabel('Green')
		ax.set_zlabel('Blue')
		ax.set_xlim(min(red_values), max(red_values))
		ax.set_ylim(min(green_values), max(green_values))
		ax.set_zlim(min(blue_values), max(blue_values))
		title(self.name)
		# plot 3D values
		ax.scatter(red_values, green_values, blue_values, c=colors, marker="o")
		matplotlib.pyplot.show()
