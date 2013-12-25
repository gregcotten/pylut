from LUTFormatter import LUTFormatter
from cStringIO import StringIO

class LUTFormatterLustre3DL(LUTFormatter):

	@staticmethod
	def FromFile(filePath):
		f = open(filePath, 'rU')
		lines = f.readlines()
		f.close()
		name = os.path.splitext(os.path.basename(filePath))[0]
		return LUTFormatterLustre3DL.FromLines(lines, name)
		
	@staticmethod
	def ToFile(lut, fileOutPath, options = {}):
		lutFile = open(fileOutPath, 'w')
		lutFile.write(LUTFormatterLustre3DL.ToFileString(lut, options))
		lutFile.close()

	@staticmethod
	def FromLines(lutFileLines, name = None):
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
	def ToFileString(lut, options = {}):
		depth = options.get('bitdepth', 16)
		string = StringIO()

		cubeSize = lut.cubeSize
		inputDepth = math.log(cubeSize-1, 2)

		if int(inputDepth) != inputDepth:
			raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

		string.write("3DMESH\n")
		string.write("Mesh " + str(int(inputDepth)) + " " + str(depth) + "\n")
		string.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**10 - 1)]) + "\n")

		string.write(LUTFormatterNuke3DL.LatticeTo3DLString(depth))

		string.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

		return string.getvalue()
