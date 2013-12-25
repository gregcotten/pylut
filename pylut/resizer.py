from transformer import LUTTransformer

class LUTResizer(LUTTransformer):

	def Resize(self, newCubeSize):
		"""
		Scales the lattice to a new cube size.
		"""
		if newCubeSize == self.lut.cubeSize:
			return self.lut

		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.lut.cubeSize - 1.0) / float(newCubeSize-1.0)
		for x in xrange(newCubeSize):
			for y in xrange(newCubeSize):
				for z in xrange(newCubeSize):
					newLattice[x, y, z] = self.lut.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
		return LUT(newLattice, name = self.lut.name + "_Resized"+str(newCubeSize))

	def _ResizeAndAddToData(self, newCubeSize, data, progress = False):
		"""
		Scales the lattice to a new cube size.
		"""
		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.lut.cubeSize - 1.0) / float(newCubeSize-1.0)
		maxVal = newCubeSize-1

		bar = Bar("Building search tree", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')
		try:
			for x in xrange(newCubeSize):
				if progress:
					bar.next()
				for y in xrange(newCubeSize):
					for z in xrange(newCubeSize):
						data.add(self.lut.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio).ToFloatArray(), (RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal)))
		except KeyboardInterrupt:
			bar.finish()
			raise KeyboardInterrupt
		bar.finish()
		return data
