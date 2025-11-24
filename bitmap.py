from math import ceil
from itertools import batched

class Bitmap(list):
	@staticmethod
	def create(bootsector, calculations, shift, zeroes):
		bitmap = Bitmap(
			True for _ in range(
				ceil(calculations.cluster_count / 8) * 8
			)
		)

		length = ceil(
			calculations.cluster_count / (8 * bootsector.BytesPerSector * bootsector.SectorsPerCluster)
		)

		if length > len(zeroes):
			raise Exception('Provided size is too low.')

		bitmap.chain = tuple(
			zeroes.popleft() for _ in range(length)
		)

		for address in zeroes:
			bitmap[address - 2 - calculations.fat_diff] = False
		
		return bitmap

	def write(self, fd_w, bootsector, calculations):
		iter_chain = iter(self.chain)

		for chunk_cluster in batched(self, 8 * bootsector.BytesPerSector * bootsector.SectorsPerCluster):
			fd_w.seek(
				(
					bootsector['ClusterHeapOffset'] + (next(iter_chain) - 2) * bootsector.SectorsPerCluster
				) * bootsector.BytesPerSector
			)

			for chunk_byte in batched(chunk_cluster, 8):
				byte = 0

				for i, bit in enumerate(chunk_byte):
					if bit:
						byte = byte | (1 << i)

				fd_w.write(byte.to_bytes())

