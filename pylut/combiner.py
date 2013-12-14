class LUTCombiner(LUTTransformer):

	def CombineWithLUT(self, otherLUT):
		"""
		Returns a new LUT that combines self.lut with otherLUT
		"""
		if self.lut.cubeSize is not otherLUT.cubeSize:
			raise NameError("Lattice Sizes not equivalent")
		
		
		cubeSize = self.lut.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		
		for x in xrange(cubeSize):
			for y in xrange(cubeSize):
				for z in xrange(cubeSize):
					selfColor = self.lut.lattice[x, y, z].Clamped01()
					newLattice[x, y, z] = otherLUT.ColorFromColor(selfColor)
		return LUT(newLattice, name = self.lut.name + "+" + otherLUT.name)
