class Helper:

	@staticmethod
	def EmptyLatticeOfSize(cubeSize):
		return np.zeros((cubeSize, cubeSize, cubeSize), object)

	@staticmethod
	def Indices01(cubeSize):
		indices = []
		ratio = 1.0/float(cubeSize-1)
		for i in xrange(cubeSize):
			indices.append(float(i) * ratio)
		return indices

	@staticmethod
	def Indices(cubeSize, bitdepth):
		indices = []
		for i in Indices01(cubeSize):
			indices.append(i * (2**bitdepth - 1))
		return indices

	@staticmethod
	def RemapIntTo01(val, maxVal):
		return (float(val)/float(maxVal))

	@staticmethod
	def Remap01ToInt(val, bitdepth):
		return int(val * (2**bitdepth - 1))

	@staticmethod
	def LerpColor(beginning, end, value01):
		if value01 < 0 or value01 > 1:
			raise NameError("Improper Lerp")
		return Color(Lerp1D(beginning.r, end.r, value01), Lerp1D(beginning.g, end.g, value01), Lerp1D(beginning.b, end.b, value01))

	@staticmethod
	def Lerp3D(beginning, end, value01):
		if value01 < 0 or value01 > 1:
			raise NameError("Improper Lerp")
		return [Lerp1D(beginning[0], end[0], value01), Lerp1D(beginning[1], end[1], value01), Lerp1D(beginning[2], end[2], value01)]

	@staticmethod
	def Lerp1D(beginning, end, value01):
		if value01 < 0 or value01 > 1:
			raise NameError("Improper Lerp")

		range = float(end) - float(beginning)
		return float(beginning) + float(range) * float(value01)

	@staticmethod
	def Distance3D(a, b):
		return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)

	@staticmethod
	def Clamp(value, min, max):
		if min > max:
			raise NameError("Invalid Clamp Values")
		if value < min:
			return float(min)
		if value > max:
			return float(max)
		return value
