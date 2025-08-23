from utils import Conversion
from enum import Enum
from shift import is_contiguous

class Fat(list):
	class Values(Enum):
		Reserved = object()
		End = object()
		Unused = object()
		Broken = object()

	@staticmethod
	def Generator(fd_r, bootsector):
		fd_r.seek(
			bootsector['FatOffset'] * bootsector.BytesPerSector + 4 * 2
		)

		yield from (Fat.Values.Reserved,) * 2

		for _ in range(bootsector['ClusterCount']):
			value = Conversion.u32.fd(fd_r)

			if 0xFFFFFFF8 <= value <= 0xFFFFFFFF:
				yield Fat.Values.End
			elif value == 0:
				yield Fat.Values.Unused
			elif value == 0xFFFFFFF7:
				yield Fat.Values.Broken
			else:
				yield value

	@staticmethod
	def create(fd_r, bootsector):
		return Fat(
			Fat.Generator(fd_r, bootsector)
		)

	def chain(self, address):
		chain = [address]

		while (value := self[chain[-1]]) != Fat.Values.End:
			chain.append(value)

		return tuple(chain)

	def broken(self):
		return tuple(
			i for i, value in enumerate(self) if value == Fat.Values.Broken
		)

	def update(self, calculations, structure, shift):
		broken_new = tuple(
			address - calculations.fat_diff
			for address in self.broken()
			if 2 <= address - calculations.fat_diff <= 1 + calculations.cluster_count
		)
	
		self[:] = [Fat.Values.Reserved] * 2 + [Fat.Values.Unused] * calculations.cluster_count

		for address in broken_new:
			self[address] = Fat.Values.Broken

		for position, chain in (structure | shift).items():
			if not is_contiguous(chain) or position in (structure.position_bitmap, structure.position_table, None):
				chain_new = (address - calculations.fat_diff for address in chain)

				previous = next(chain_new)
				for address in chain_new:
					self[previous] = address
					previous = address
				self[previous] = Fat.Values.End

	def ReverseGenerator(self):
		yield from (0xFFFFFFF8, 0xFFFFFFFF)

		for value in self[2:]:
			if value == Fat.Values.End:
				yield 0xFFFFFFFF
			elif value == Fat.Values.Unused:
				yield 0
			elif value == Fat.Values.Broken:
				yield 0xFFFFFFF7
			else:
				yield value

	def write(self, fd_w, bootsector):
		fd_w.seek(24 * bootsector.BytesPerSector)
		fd_w.write(
			b''.join(
				Conversion.u32.revert(value) for value in self.ReverseGenerator()
			)
		)

