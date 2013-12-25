#MIT License
#Authored by Greg Cotten


import os
import math
import numpy as np
import kdtree
from progress.bar import Bar
import struct

def EmptyLatticeOfSize(cubeSize):
	return np.zeros((cubeSize, cubeSize, cubeSize), object)

def Indices01(cubeSize):
	indices = []
	ratio = 1.0/float(cubeSize-1)
	for i in xrange(cubeSize):
		indices.append(float(i) * ratio)
	return indices

def Indices(cubeSize, maxVal):
	indices = []
	for i in Indices01(cubeSize):
		indices.append(int(i * (maxVal)))
	return indices


def RemapIntTo01(val, maxVal):
	return (float(val)/float(maxVal))

def Remap01ToInt(val, maxVal):
	return int(iround(float(val) * float(maxVal)))

def iround(num):
	if (num > 0):
		return int(num+.5)
	else:
		return int(num-.5)

def LerpColor(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")
	return Color(Lerp1D(beginning.r, end.r, value01), Lerp1D(beginning.g, end.g, value01), Lerp1D(beginning.b, end.b, value01))

def Lerp3D(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")
	return [Lerp1D(beginning[0], end[0], value01), Lerp1D(beginning[1], end[1], value01), Lerp1D(beginning[2], end[2], value01)]

def Lerp1D(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")

	range = float(end) - float(beginning)
	return float(beginning) + float(range) * float(value01)

def Distance3D(a, b):
	return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)

def Clamp(value, min, max):
	if min > max:
		raise NameError("Invalid Clamp Values")
	if value < min:
		return float(min)
	if value > max:
		return float(max)
	return value

def Checksum(data):
	sum = 0
	for x in data:
		sum = sum + struct.unpack("<B",x)
	return sum

def ToIntArray(string):
	array = []
	for x in string:
		array.append(ord(x))
	return array


class Color:
	"""
	RGB floating point representation of a color. 0 is absolute black, 1 is absolute white.
	Access channel data by color.r, color.g, or color.b. 
	"""
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def Clamped01(self):
		return Color(Clamp(float(self.r), 0, 1), Clamp(float(self.g), 0, 1), Clamp(float(self.b), 0, 1))

	@staticmethod
	def FromRGBInteger(r, g, b, bitdepth):
		"""
		Instantiates a floating point color from RGB integers at a bitdepth.
		"""
		maxBits = 2**bitdepth - 1
		return Color(RemapIntTo01(r, maxBits), RemapIntTo01(g, maxBits), RemapIntTo01(b, maxBits))

	@staticmethod
	def FromFloatArray(array):
		"""
		Creates Color from a list or tuple of 3 floats.
		"""
		return Color(array[0], array[1], array[2])

	@staticmethod
	def FromRGBIntegerArray(array, bitdepth):
		"""
		Creates Color from a list or tuple of 3 RGB integers at a specified bitdepth.
		"""
		maxBits = 2**bitdepth - 1
		return Color(RemapIntTo01(array[0], maxBits), RemapIntTo01(array[1], maxBits), RemapIntTo01(array[2], maxBits))

	
	def ToFloatArray(self):
		"""
		Creates a tuple of 3 floating point RGB values from the floating point color.
		"""
		return (self.r, self.g, self.b)

	def ToRGBIntegerArray(self, bitdepth):
		"""
		Creates a list of 3 RGB integer values at specified bitdepth from the floating point color.
		"""
		maxVal = (2**bitdepth - 1)
		return (Remap01ToInt(self.r, maxVal), Remap01ToInt(self.g, maxVal), Remap01ToInt(self.b, maxVal))

	def ClampColor(self, min, max):
		"""
		Returns a clamped color.
		"""
		return Color(Clamp(self.r, min.r, max.r), Clamp(self.g, min.g, max.g), Clamp(self.b, min.b, max.b))

	def DistanceToColor(color):
		if isinstance(color, Color):
			return Distance3D(self.ToFloatArray(), color.ToFloatArray())
		return NotImplemented
	
	def __add__(self, color):
		return Color(self.r + color.r, self.g + color.g, self.b + color.b)


	def __sub__(self, color):
		return Color(self.r - color.r, self.g - color.g, self.b - color.b)
	
	def __mul__(self, color):
		if not isinstance(color, Color):
			mult = float(color)
			return Color(self.r * mult, self.g * mult, self.b * mult)
		return Color(self.r * color.r, self.g * color.g, self.b * color.b)

	def __eq__(self, color):
		if isinstance(color, Color):
			return self.r == color.r and self.g == color.g and self.b == color.b
		return NotImplemented

	def __ne__(self, color):
		result = self.__eq__(color)
		if result is NotImplemented:
			return result
		return not result
	
	def __str__(self):
		return "(" + str(self.r) + ", " + str(self.g) + ", " + str(self.b) + ")"
	
	def FormattedAsFloat(self, format = '{:1.6f}'):
		return format.format(self.r) + " " + format.format(self.g) + " " + format.format(self.b)
	
	def FormattedAsInteger(self, maxVal):
		rjustValue = len(str(maxVal)) + 1
		return str(Remap01ToInt(self.r, maxVal)).rjust(rjustValue) + " " + str(Remap01ToInt(self.g, maxVal)).rjust(rjustValue) + " " + str(Remap01ToInt(self.b, maxVal)).rjust(rjustValue)

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
		
	def Resize(self, newCubeSize):
		"""
		Scales the lattice to a new cube size.
		"""
		if newCubeSize == self.cubeSize:
			return self

		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.cubeSize - 1.0) / float(newCubeSize-1.0)
		for x in xrange(newCubeSize):
			for y in xrange(newCubeSize):
				for z in xrange(newCubeSize):
					newLattice[x, y, z] = self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
		return LUT(newLattice, name = self.name + "_Resized"+str(newCubeSize))

	def _ResizeAndAddToData(self, newCubeSize, data, progress = False):
		"""
		Scales the lattice to a new cube size.
		"""
		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.cubeSize - 1.0) / float(newCubeSize-1.0)
		maxVal = newCubeSize-1

		bar = Bar("Building search tree", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')
		try:
			for x in xrange(newCubeSize):
				if progress:
					bar.next()
				for y in xrange(newCubeSize):
					for z in xrange(newCubeSize):
						data.add(self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio).ToFloatArray(), (RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal)))
		except KeyboardInterrupt:
			bar.finish()
			raise KeyboardInterrupt
		bar.finish()
		return data

	def Reverse(self, progress = False):
		"""
		Reverses a LUT. Warning: This can take a long time depending on if the input/output is a bijection.
		"""
		tree = self.KDTree(progress)
		newLattice = EmptyLatticeOfSize(self.cubeSize)
		maxVal = self.cubeSize - 1
		bar = Bar("Searching for matches", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')
		try:
			for x in xrange(self.cubeSize):
				if progress:
					bar.next()
				for y in xrange(self.cubeSize):
					for z in xrange(self.cubeSize):
						newLattice[x, y, z] = Color.FromFloatArray(tree.search_nn((RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal))).aux)
		except KeyboardInterrupt:
			bar.finish()
			raise KeyboardInterrupt
		bar.finish()
		return LUT(newLattice, name = self.name +"_Reverse")
	
	def KDTree(self, progress = False):
		tree = kdtree.create(dimensions=3)
		
		tree = self._ResizeAndAddToData(self.cubeSize*3, tree, progress)
	
		return tree

		
	def CombineWithLUT(self, otherLUT):
		"""
		Combines LUT with another LUT.
		"""
		if self.cubeSize is not otherLUT.cubeSize:
			raise NameError("Lattice Sizes not equivalent")
		
		
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					selfColor = self.lattice[x, y, z].Clamped01()
					newLattice[x, y, z] = otherLUT.ColorFromColor(selfColor)
		return LUT(newLattice, name = self.name + "+" + otherLUT.name)

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

	def _LatticeTo3DLString(self, bitdepth):
		"""
		Used for internal creating of 3DL files.
		"""
		string = ""
		cubeSize = self.cubeSize
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex / (cubeSize*cubeSize)
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex % cubeSize

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()
			
			string += latticePointColor.FormattedAsInteger(2**bitdepth-1) + "\n"
		
		return string

	
	def ToLustre3DLFile(self, fileOutPath, bitdepth = 12):
		cubeSize = self.cubeSize
		inputDepth = math.log(cubeSize-1, 2)

		if int(inputDepth) != inputDepth:
			raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

		lutFile = open(fileOutPath, 'w')

		lutFile.write("3DMESH\n")
		lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**10 - 1)]) + "\n")
		
		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

		lutFile.close()

	def ToNuke3DLFile(self, fileOutPath, bitdepth = 16):
		cubeSize = self.cubeSize

		lutFile = open(fileOutPath, 'w')

		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**bitdepth - 1)]) + "\n")

		lutFile.write(self._LatticeTo3DLString(bitdepth))

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

	def ToFSIDatFile(self, datFileOutPath):
		import tempfile
		cubeSize = 64
		datFile = open(datFileOutPath, 'w+b')
		if self.cubeSize is not 64:
			lut = self.Resize(64)
		else:
			lut = self
		lut_checksum = 0
		lut_bytes = []
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex / (cubeSize*cubeSize)

			latticePointColor = lut.lattice[redIndex, greenIndex, blueIndex].Clamped01()
			
			rgb_packed =( Remap01ToInt(latticePointColor.r, 1008) | Remap01ToInt(latticePointColor.g, 1008) << 10 | Remap01ToInt(latticePointColor.g, 1008) << 20 )
			rgb_packed_binary = struct.pack("<L", rgb_packed)
			lut_checksum = (lut_checksum + rgb_packed) % 4294967296
			lut_bytes.append(rgb_packed_binary)

		header_bytes = []
		header_bytes.append(struct.pack("<L",0x42340299))#magic number
		header_bytes.append(struct.pack("<L",0x01000002))#spec version number?
		header_bytes.append(bytearray("None".ljust(16)))#monitor ID (real ID not required if dit.dat file)
		header_bytes.append(bytearray("V1.0".ljust(16)))#lut version number
		header_bytes.append(struct.pack("<L", lut_checksum))
		header_bytes.append(struct.pack("<L",1048576))#number of bytes in LUT (always the same)
		header_bytes.append(bytearray("pylut generated".ljust(16)))#author
		header_bytes.append(bytearray(" ".ljust(63)))#reserved

		header_checksum = 0

		for item in header_bytes:
			if isinstance(item, str):
				itemSum = sum(map(ord,item)) 
			else:
				itemSum = sum(item)
			header_checksum = (header_checksum + itemSum) % 256

		header_bytes.append(struct.pack("<B",header_checksum))


		[datFile.write(x) for x in header_bytes]
		[datFile.write(x) for x in lut_bytes]

		datFile.close()



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
	def FromNuke3DLFile(lutFilePath):
		lutFile = open(lutFilePath, 'rU')
		lutFileLines = lutFile.readlines()
		lutFile.close()

		meshLineIndex = 0
		cubeSize = -1
		lineSkip = 0

		for line in lutFileLines:
			if "#" in line or line == "\n":
				meshLineIndex += 1
	
		outputDepth = int(math.log(int(lutFileLines[meshLineIndex].split()[-1])+1,2))
		cubeSize = len(lutFileLines[meshLineIndex].split())
		
	
		if cubeSize == -1:
			raise NameError("Invalid .3dl file.")

		lattice = EmptyLatticeOfSize(cubeSize)
		currentCubeIndex = 0

		# for line in lutFileLines[meshLineIndex+1:]:
		for line in lutFileLines[meshLineIndex+1:]:
			# print line
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

	@staticmethod
	def FromFSIDatFile(datFilePath):
		datBytes = bytearray(open(datFilePath, 'r').read())
		cubeSize = 64
		lattice = EmptyLatticeOfSize(cubeSize)
		lutBytes = datBytes[128:]
		for currentCubeIndex in xrange(len(lutBytes)/4):
			rgb_packed = np.uint32(struct.unpack("<L", lutBytes[currentCubeIndex*4:(currentCubeIndex*4)+4])[0])

			redValue = RemapIntTo01(rgb_packed & 1023, 1008)
			greenValue = RemapIntTo01(rgb_packed >> 10 & 1023, 1008)
			blueValue = RemapIntTo01(rgb_packed >> 20 & 1023, 1008)

			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex / (cubeSize*cubeSize)

			lattice[redIndex, greenIndex, blueIndex] = Color(redValue, greenValue, blueValue)

		return LUT(lattice, name = os.path.splitext(os.path.basename(datFilePath))[0])




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
