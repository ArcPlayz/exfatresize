from math import ceil
from utils import ReturningGenerator
from collections import namedtuple, deque

def is_contiguous(chain):
	previous = chain[0]

	for address in chain[1:]:
		if address - previous > 1:
			return False

		previous = address

	return True

Calculations = namedtuple(
	'Calculations', ('cluster_count', 'fat_length', 'cluster_heap_offset', 'fat_diff', 'shrink_diff')
)
def calculate(sector_count, bootsector):
	cluster_count = 0

	while True:
		fat_length = ceil(cluster_count * 4 / bootsector.BytesPerSector)

		_fat_diff = max(
			fat_length - (bootsector['ClusterHeapOffset'] - 24),
			0
		)
		fat_diff =  ceil(_fat_diff / bootsector.SectorsPerCluster)

		shrink_diff = min(
			cluster_count - bootsector['ClusterCount'],
			0
		)

		cluster_heap_offset = bootsector['ClusterHeapOffset'] if not fat_diff else bootsector['ClusterHeapOffset'] + _fat_diff

		if cluster_heap_offset + (cluster_count + 1) * bootsector.SectorsPerCluster > sector_count:
			return Calculations(cluster_count, fat_length, cluster_heap_offset, fat_diff, shrink_diff)
		else:
			cluster_count += 1

def Shift(bootsector, calculations, fat, structure):
	zeroes = set(
		2 + calculations.fat_diff + i
		for i in range(calculations.cluster_count)
	)

	to_move = []

	for position, chain in structure.items():
		if (
			calculations.fat_diff and chain[0] < 2 + calculations.fat_diff
		) or (
			calculations.shrink_diff and chain[-1] > 1 + calculations.cluster_count
		):
			to_move.append(
				(position, len(chain))
			)
		else:
			zeroes -= set(chain)

	zeroes = deque(
		sorted(zeroes)
	)

	_shift = {}

	for position, length in to_move:
		if length > len(zeroes):
			raise Exception('Provided size is too low.')

		_shift[position] = tuple(
			zeroes.popleft() for _ in range(length)
		)

	return _shift, zeroes

