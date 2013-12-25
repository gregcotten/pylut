from LUTFormatter import LUTFormatter

class LUTFormatterNuke3DL(LUTFormatter):

	@staticmethod
	def FromLines(lutFileLines, name = None):

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

		return LUT(lattice, name = name)

	@staticmethod
	def ToFileString(lut, options = {}):
		depth = options.get('bitdepth', 16)
		string = ' '.join([str(int(x)) for x in Indices(cubeSize, 2**depth - 1)]) + "\n"
		string += LatticeTo3DLString(lut, depth)
		return string

	@staticmethod
	def LatticeTo3DLString(lut, bitdepth):
		string = ""
		cubeSize = self.cubeSize
		maxVal = 2**bitdepth-1
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex / (cubeSize*cubeSize)
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex % cubeSize

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()
			
			string += latticePointColor.FormattedAsInteger(maxVal) + "\n"
		
		return string

