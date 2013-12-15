class LUTFormatter:

	@staticmethod
	def FromFile(filePath):
		f = open(filePath, 'rU')
		lines = f.readlines()
		f.close()
		name = os.path.splitext(os.path.basename(filePath))[0]
		return FromLines(lines, name)

	@staticmethod
	def FromLines(lines, name = None):
		# Stub, subclass
		return None

	@staticmethod
	def ToFile(lut, fileOutPath, options = {}):
		lutFile = open(fileOutPath, 'w')
		lutFile.write(ToFileString(lut, options))
		lutFile.close()

	@staticmethod
	def ToFileString(lut, options = {}):
		return "Unimplemented"