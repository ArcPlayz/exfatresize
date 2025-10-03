from shift import is_contiguous
from utils import Conversion
from os import SEEK_CUR
from math import ceil

def alter(fd_w, sector_count, bootsector, fat, structure, calculations, shift, bitmap):
	entries = shift if not calculations.fat_diff else structure | shift

	if entries: print('- Updating directory entries...')

	root_chain = None
	for position, chain in (*entries.items(), (structure.position_bitmap, bitmap.chain)):
		if not position:
			root_chain = chain
			continue

		fd_w.seek(
			(
				bootsector['ClusterHeapOffset'] + (position.address - 2) * bootsector.SectorsPerCluster
			) * bootsector.BytesPerSector + position.i * 32
		)
		data = bytearray(fd_w.read(32))

		if position not in (structure.position_bitmap, structure.position_table):
			data[1] = (data[1] | 0b10) if is_contiguous(chain) else (data[1] & ~0b10)

		elif position == structure.position_bitmap:
			data[24:32] = Conversion.u64.revert(
				ceil(calculations.cluster_count / 8)
			)

		data[20:24] = Conversion.u32.revert(chain[0] - calculations.fat_diff)

		fd_w.seek(-32, SEEK_CUR)
		fd_w.write(data)

	if shift:
		print('- Moving clusters to new positions...')

		for f, t in sorted(
			(
				(f, t)
				for position in shift
				for f, t in zip(structure[position], shift[position])
			),
			key = lambda f_t: f_t[0],
			reverse = calculations.fat_diff
		):
			fd_w.seek(
				(
					bootsector['ClusterHeapOffset'] + (f - 2) * bootsector.SectorsPerCluster
				) * bootsector.BytesPerSector
			)
			cluster = fd_w.read(bootsector.SectorsPerCluster * bootsector.BytesPerSector)
			fd_w.seek(
				(
					bootsector['ClusterHeapOffset'] + (t - 2) * bootsector.SectorsPerCluster
				) * bootsector.BytesPerSector
			)
			fd_w.write(cluster)

	print('- Writing new allocation bitmap...')

	bitmap.write(fd_w, bootsector, calculations)

	print('- Writing new FAT...')

	fat.write(fd_w, bootsector)

	print('- Updating bootregion...')

	bootsector['VolumeLength'] = sector_count
	bootsector['FatOffset'] = 24
	bootsector['FatLength'] = calculations.fat_length
	bootsector['ClusterHeapOffset'] = calculations.cluster_heap_offset
	bootsector['ClusterCount'] = calculations.cluster_count
	if root_chain:
		bootsector['FirstClusterOfRootDirectory'] = root_chain[0]
	bootsector['PercentInUse'] = sum(
		len(chain) for chain in (structure | shift).values()
	) * 100 // calculations.cluster_count

	bootsector.write(fd_w)
