from transformer import LUTTransformer
import kdtree
from progress.bar import Bar

class LUTReverser(LUTTransformer):

	def Reverse(self, progress = False):
		"""
		Reverses a LUT. Warning: This can take a long time depending on if the input/output is a bijection.
		"""
		tree = self.BuildKDTree(progress)
		newLattice = EmptyLatticeOfSize(self.lut.cubeSize)
		maxVal = self.lut.cubeSize - 1
		bar = Bar("Searching for matches", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')
		try:
			for x in xrange(self.lut.cubeSize):
				if progress:
					bar.next()
				for y in xrange(self.lut.cubeSize):
					for z in xrange(self.lut.cubeSize):
						newLattice[x, y, z] = Color.FromFloatArray(tree.search_nn((RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal))).aux)
		except KeyboardInterrupt:
			bar.finish()
			raise KeyboardInterrupt
		bar.finish()
		return LUT(newLattice, name = self.lut.name +"_Reverse")
	
	def BuildKDTree(self, progress = False):
		tree = kdtree.create(dimensions=3)
		tree = self.lut._ResizeAndAddToData(self.cubeSize*3, tree, progress)
		return tree
