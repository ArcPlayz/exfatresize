from utils import Conversion, ReturningGenerator
from math import ceil
from collections import namedtuple

Position = namedtuple('Position', ('address', 'i'))

class Structure(dict):
	@staticmethod
	def EntryIterator(fd_r, bootsector, fat, chain):
		for address in chain:
			fd_r.seek(
				(
					bootsector['ClusterHeapOffset'] + (address - 2) * bootsector.SectorsPerCluster
				) * bootsector.BytesPerSector
			)

			for i in range(
				bootsector.SectorsPerCluster * bootsector.BytesPerSector // 32
			):
				yield fd_r.read(32), Position(address, i)

	@staticmethod
	@ReturningGenerator.create
	def Generator(fd_r, bootsector, fat, chain = None):
		if chain == None:
			chain = fat.chain(bootsector['FirstClusterOfRootDirectory'])

			yield None, chain

		previous = None

		position_bitmap = None
		position_table = None

		for data, position in Structure.EntryIterator(fd_r, bootsector, fat, chain):
			match data[0]:
				case 0:
					break
				case 0xC0:
					if not data[1] & 0b10:
						chain = fat.chain(Conversion.u32(data, 20))
					else:
						chain = tuple(
							Conversion.u32(data, 20) + i
							for i in range(
								ceil(
									Conversion.u64(data, 24) / (bootsector.SectorsPerCluster * bootsector.BytesPerSector)
								)
							)
						)

					yield position, chain

					if Conversion.u16(previous, 4) & 0b10000:
						pos = fd_r.tell()

						yield from Structure.Generator(fd_r, bootsector, fat, chain)

						fd_r.seek(pos)
				case 0x81:
					position_bitmap = position
				case 0x82:
					yield position, fat.chain(Conversion.u32(data, 20))

					position_table = position

			previous = data

		return position_bitmap, position_table

	@staticmethod
	def create(fd_r, bootsector, fat):
		ret = Structure(
			_generator := Structure.Generator(fd_r, bootsector, fat)
		)

		ret.position_bitmap, ret.position_table = _generator.returned

		return ret

