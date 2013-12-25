from LUTFormatter import LUTFormatter
from cStringIO import StringIO
import os
from helper import Helper

class LUTFormatterCube(LUTFormatter):

	@staticmethod
	def FromFile(filePath):
		f = open(filePath, 'rU')
		lines = f.readlines()
		f.close()
		name = os.path.splitext(os.path.basename(filePath))[0]
		return LUTFormatterCube.FromLines(lines, name)
	@staticmethod
	def ToFile(lut, fileOutPath, options = {}):
		lutFile = open(fileOutPath, 'w')
		lutFile.write(LUTFormatterCube.ToFileString(lut, options))
		lutFile.close()

	@staticmethod
	def FromLines(cubeFileLines, name = None):
		cubeSizeLineIndex = 0
		cubeSize = -1

		for line in cubeFileLines:
			if "LUT_3D_SIZE" in line:
				cubeSize = int(line.split()[1])
				break
			cubeSizeLineIndex += 1
		if cubeSize == -1:
			raise NameError("Invalid .cube file.")

		lattice = Helper.EmptyLatticeOfSize(cubeSize)
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

		return LUT(lattice, name)


	@staticmethod
	def ToFileString(lut, options = {}):
		string = StringIO()
		cubeSize = self.cubeSize
		string.write("LUT_3D_SIZE " + str(cubeSize) + "\n")

		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) / (cubeSize) )
			blueIndex = currentCubeIndex / (cubeSize*cubeSize)

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()

			string.write( latticePointColor.FormattedAsFloat() )

			if(currentCubeIndex != cubeSize**3 - 1):
				string.write("\n")

		return string.getvalue()

