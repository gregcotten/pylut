from helper import Helper

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
		return Color(Helper.Clamp(float(self.r), 0, 1), Helper.Clamp(float(self.g), 0, 1), Helper.Clamp(float(self.b), 0, 1))

	@staticmethod
	def FromRGBInteger(r, g, b, bitdepth):
		"""
		Instantiates a floating point color from RGB integers at a bitdepth.
		"""
		maxBits = 2**bitdepth - 1
		return Color(Helper.RemapIntTo01(r, maxBits), Helper.RemapIntTo01(g, maxBits), Helper.RemapIntTo01(b, maxBits))

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
		return Color(Helper.RemapIntTo01(array[0], maxBits), Helper.RemapIntTo01(array[1], maxBits), Helper.RemapIntTo01(array[2], maxBits))


	def ToFloatArray(self):
		"""
		Creates a tuple of 3 floating point RGB values from the floating point color.
		"""
		return (self.r, self.g, self.b)

	def ToRGBIntegerArray(self, bitdepth):
		"""
		Creates a list of 3 RGB integer values at specified bitdepth from the floating point color.
		"""
		return (Helper.Remap01ToInt(self.r, bitdepth), Helper.Remap01ToInt(self.g, bitdepth), Helper.Remap01ToInt(self.b, bitdepth))

	def ClampColor(self, min, max):
		"""
		Returns a clamped color.
		"""
		return Color(Clamp(self.r, min.r, max.r), Clamp(self.g, min.g, max.g), Clamp(self.b, min.b, max.b))

	def DistanceToColor(color):
		if isinstance(color, Color):
			return Helper.Distance3D(self.ToFloatArray(), color.ToFloatArray())
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

	def FormattedAsInteger(self, bitdepth):
		rjustValue = len(str(2**bitdepth - 1)) + 1
		return str(Helper.Remap01ToInt(self.r, bitdepth)).rjust(rjustValue) + " " + str(Helper.Remap01ToInt(self.g, bitdepth)).rjust(rjustValue) + " " + str(Helper.Remap01ToInt(self.b, bitdepth)).rjust(rjustValue)
