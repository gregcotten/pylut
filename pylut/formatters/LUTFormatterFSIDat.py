from LUTFormatter import LUTFormatter

class LUTFormatterFSIDat(LUTFormatter):

	@staticmethod
	def FromFile(filePath):
		import struct
		datBytes = bytearray(open(filePath, 'r').read())
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

		return LUT(lattice, name = os.path.splitext(os.path.basename(filePath))[0])

	@staticmethod
	def ToFile(lut, fileOutPath, options = {}):
		cubeSize = 64
		datFile = open(fileOutPath, 'w+b')
		if lut.cubeSize is not 64:
			lut = lut.Resize(64)
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

