#MIT License
#Authored by Greg Cotten


import os
import math
import numpy as np

def EmptyLatticeOfSize(cubeSize):
	return np.zeros((cubeSize, cubeSize, cubeSize), object)

def Indices01(cubeSize):
	indices = []
	ratio = 1.0/float(cubeSize-1)
	for i in xrange(cubeSize):
		indices.append(float(i) * ratio)
	return indices

def Indices(cubeSize, bitdepth):
	indices = []
	for i in Indices01(cubeSize):
		indices.append(i * (2**bitdepth - 1))
	return indices


def RemapIntTo01(val, maxVal):
	return (float(val)/float(maxVal))

def Remap01ToInt(val, bitdepth):
	return int(val * (2**bitdepth - 1))

def LerpColor(beginning, end, value01):
	return Color.FromArray(Lerp3D(beginning.ToArray(), end.ToArray(), value01))

def Lerp3D(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")
	return [Lerp1D(beginning[0], end[0], value01), Lerp1D(beginning[1], end[1], value01), Lerp1D(beginning[2], end[2], value01)]

def Lerp1D(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")

	range = float(end) - float(beginning)
	return float(beginning) + float(range) * float(value01)

def Clamp(value, min, max):
	if min > max:
		raise NameError("Invalid Clamp Values")
	if value < min:
		return float(min)
	if value > max:
		return float(max)
	return value

class Color:
	def __init__(self, r, g, b):
		self.SetRGB(r,g,b)

	def SetRGB(self, r, g, b):
		self.r = Clamp(float(r), 0, 1)
		self.g = Clamp(float(g), 0, 1)
		self.b = Clamp(float(b), 0, 1)
		if 0 > r > 1 or 0 > g > 1 or 0 > b > 1:
			print "Warning: (" + str(r) + ", " + str(g) + ", " + str(b) + ") out of range and clamped to " + self

	@staticmethod
	def FromInteger(r, g, b, bitdepth):
		return Color(float(r)/float(2**bitdepth - 1), float(g)/float(2**bitdepth - 1), float(b)/float(2**bitdepth - 1))

	@staticmethod
	def FromArray(array):
		return Color(array[0], array[1], array[2])

	def ToArray(self):
		return [self.r, self.g, self.b]

	def Clamp(self, min, max):
		return Color(Clamp(self.r, min, max), Clamp(self.g, min, max), Clamp(self.b, min, max))

	def ClampRed(self, min, max):
		if min > max:
			raise NameError("Invalid Clamp Values")
		return Color(Clamp(self.r, min, max), self.g, self.b)

	def ClampGreen(self, min, max):
		if min > max:
			raise NameError("Invalid Clamp Values")
		return Color(self.r, Clamp(self.g, min, max), self.b)

	def ClampBlue(self, min, max):
		if min > max:
			raise NameError("Invalid Clamp Values")
		return Color(self.r, self.g, Clamp(self.b, min, max))
	
	def __add__(self, color):
		if "Color" not in color.__class__.__name__:
			return Color(self.r + color, self.g + color, self.b + color)
		return Color(self.r + color.r, self.g + color.g, self.b + color.b)


	def __sub__(self, color):
		return Color(self.r - color.r, self.g - color.g, self.b - color.b)
	
	def __mul__(self, color):
		if "Color" not in color.__class__.__name__:
			mult = float(color)
			return Color(self.r * mult, self.g * mult, self.b * mult)
		return Color(self.r * color.r, self.g * color.g, self.b * color.b)
	
	def __str__(self):
		return "(" + str(self.r) + ", " + str(self.g) + ", " + str(self.b) + ")"
	def FormattedAsFloat(self, format = '{:1.6f}'):
		return format.format(self.r) + " " + format.format(self.g) + " " + format.format(self.b)
	def FormattedAsInteger(self, bitdepth):
		rjustValue = len(str(2**bitdepth - 1)) + 1
		return str(Remap01ToInt(self.r, bitdepth)).rjust(rjustValue) + " " + str(Remap01ToInt(self.g, bitdepth)).rjust(rjustValue) + " " + str(Remap01ToInt(self.b, bitdepth)).rjust(rjustValue)

class LUT:
	def __init__(self, lattice):
		self.lattice = lattice

	def LatticeSize(self):
		return self.lattice.shape[0]

	def Resize(self, newCubeSize):
		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.LatticeSize() - 1.0) / float(newCubeSize-1.0)
		for x in xrange(newCubeSize):
			for y in xrange(newCubeSize):
				for z in xrange(newCubeSize):
					newLattice[x, y, z] = self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
		return LUT(newLattice)
		
	def CombineWithLUT(self, otherLUT):
		if self.LatticeSize() is not otherLUT.LatticeSize():
			raise NameError("Lattice Sizes not equivalent")
		
		
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					selfLatticePoint = self.lattice[x, y, z]
					newLattice[x, y, z] = otherLUT.ColorAtInterpolatedLatticePoint(selfLatticePoint.r * (cubeSize-1), selfLatticePoint.g * (cubeSize-1), selfLatticePoint.b * (cubeSize-1))
		return LUT(newLattice)

	def ClampRGB(self, min, max):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					newLattice[x, y, z] = self.ColorAtLatticePoint(x, y, z).Clamp(min, max)
		return LUT(newLattice)

	def ClampRed(self, min, max):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					newLattice[x, y, z] = self.ColorAtLatticePoint(x, y, z).ClampRed(min, max)
		return LUT(newLattice)

	def ClampGreen(self, min, max):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					newLattice[x, y, z] = self.ColorAtLatticePoint(x, y, z).ClampGreen(min, max)
		return LUT(newLattice)

	def ClampBlue(self, min, max):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					newLattice[x, y, z] = self.ColorAtLatticePoint(x, y, z).ClampBlue(min, max)
		return LUT(newLattice)

	def _LatticeTo3DLString(self, bitdepth):
		string = ""
		cubeSize = self.LatticeSize()
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex / (cubeSize*cubeSize)
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex % cubeSize

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex]
			
			string += latticePointColor.FormattedAsInteger(bitdepth) + "\n"
		
		return string

	
	def ToLustre3DLFile(self, fileOutPath, bitdepth = 12):
		cubeSize = self.LatticeSize()
		inputDepth = math.log(cubeSize-1, 2)

		if int(inputDepth) != inputDepth:
			raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

		lutFile = open(fileOutPath, 'w')

		lutFile.write("3DMESH\n")
		lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
		lutFile.write(Indices(10) + "\n\n")
		
		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

		lutFile.close()

	def ToNuke3DLFile(self, fileOutPath, bitdepth = 16):
		cubeSize = self.LatticeSize()

		lutFile = open(fileOutPath, 'w')

		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, bitdepth)]) + "\n")

		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.close()
	
	def ToCubeFile(self, cubeFileOutPath):
		cubeSize = self.LatticeSize()
		cubeFile = open(cubeFileOutPath, 'w')
		cubeFile.write("LUT_3D_SIZE " + str(cubeSize) + "\n")
		
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex / (cubeSize*cubeSize)

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex]
			
			cubeFile.write( latticePointColor.FormattedAsFloat() )
			
			if(currentCubeIndex != cubeSize**3 - 1):
				cubeFile.write("\n")

		cubeFile.close()


	def ColorAtRGB01(self, r, g, b):
		cubeSize = self.LatticeSize()
		return self.ColorAtInterpolatedLatticePoint(r * (cubeSize-1), g * (cubeSize-1), b * (cubeSize-1))

	def ColorAtRGBInt(self, r, g, b, bitdepth):
		maximumBits = 2**bitdepth - 1
		return self.ColorAtRGB01(RemapIntTo01(r, maximumBits), RemapIntTo01(g, maximumBits), RemapIntTo01(b, maximumBits))

	#integer input from 0 to cubeSize-1
	def ColorAtLatticePoint(self, redPoint, greenPoint, bluePoint):
		cubeSize = self.LatticeSize()
		if redPoint > cubeSize-1 or greenPoint > cubeSize-1 or bluePoint > cubeSize-1:
			raise NameError("Point Out of Bounds: (" + str(redPoint) + ", " + str(greenPoint) + ", " + str(bluePoint) + ")")

		return self.lattice[redPoint, greenPoint, bluePoint]

	#float input from 0 to cubeSize-1
	def ColorAtInterpolatedLatticePoint(self, redPoint, greenPoint, bluePoint):
		cubeSize = self.LatticeSize()

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
		identityLattice = EmptyLatticeOfSize(cubeSize)
		indices01 = Indices01(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					identityLattice[r, g, b] = Color(indices01[r], indices01[g], indices01[b])
		return LUT(identityLattice)

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

		maximumBits = 2**outputDepth - 1
		lattice = EmptyLatticeOfSize(cubeSize)
		currentCubeIndex = 0
		
		for line in lutFileLines[meshLineIndex+1:]:
			if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
				#valid cube line
				redValue = RemapIntTo01(line.split()[0], maximumBits)
				greenValue = RemapIntTo01(line.split()[1], maximumBits)
				blueValue = RemapIntTo01(line.split()[2], maximumBits)

				redIndex = currentCubeIndex / (cubeSize*cubeSize)
				greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
				blueIndex = currentCubeIndex % cubeSize

				lattice[redIndex, greenIndex, blueIndex] = Color(redValue, greenValue, blueValue)
				currentCubeIndex += 1

		return LUT(lattice)

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
				redValue = RemapIntTo01(line.split()[0], 2**outputDepth - 1)
				greenValue = RemapIntTo01(line.split()[1], 2**outputDepth - 1)
				blueValue = RemapIntTo01(line.split()[2], 2**outputDepth - 1)

				redIndex = currentCubeIndex / (cubeSize*cubeSize)
				greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
				blueIndex = currentCubeIndex % cubeSize

				lattice[redIndex, greenIndex, blueIndex] = Color(redValue, greenValue, blueValue)
				currentCubeIndex += 1
		return LUT(lattice)

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

		return LUT(lattice)

	def AddToEachPoint(self, color):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] + color
		return LUT(newLattice)

	def SubtractFromEachPoint(self, color):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] - color
		return LUT(newLattice)

	def MultiplyEachPoint(self, color):
		cubeSize = self.LatticeSize()
		newLattice = EmptyLatticeOfSize(cubeSize)
		for r in xrange(cubeSize):
			for g in xrange(cubeSize):
				for b in xrange(cubeSize):
					newLattice[r, g, b] = self.lattice[r, g, b] * color
		return LUT(newLattice)


	def __add__(self, other):
		className = other.__class__.__name__
		if "Color" in className:
			return self.AddToEachPoint(other)

		if self.LatticeSize() is not other.LatticeSize():
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice + other.lattice)

	def __sub__(self, other):
		className = other.__class__.__name__
		if "Color" in className:
			return self.SubtractFromEachPoint(other)

		if self.LatticeSize() is not other.LatticeSize():
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice - other.lattice)

	def __mul__(self, other):
		className = other.__class__.__name__
		if "Color" in className or "float" in className:
			return self.MultiplyEachPoint(other)

		if self.LatticeSize() is not other.LatticeSize():
			raise NameError("Lattice Sizes not equivalent")

		return LUT(self.lattice * other.lattice)
