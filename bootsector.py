from utils import Conversion

class Bootsector(dict):
	FIELDS = (
		('FileSystemName', 3, Conversion.u64),
		('VolumeLength', 72, Conversion.u64),
		('FatOffset', 80, Conversion.u32),
		('FatLength', 84, Conversion.u32),
		('ClusterHeapOffset', 88, Conversion.u32),
		('ClusterCount', 92, Conversion.u32),
		('FirstClusterOfRootDirectory', 96, Conversion.u32),
		('BytesPerSectorShift', 108, Conversion.u8),
		('SectorsPerClusterShift', 109, Conversion.u8),
		('NumberOfFats', 110, Conversion.u8),
		('PercentInUse', 112, Conversion.u8),
	)

	@staticmethod
	def Generator(fd_r):
		for name, offset, size in Bootsector.FIELDS:
			fd_r.seek(offset)
			yield (name, size.fd(fd_r))

	@staticmethod
	def create(fd_r):
		return Bootsector(
			Bootsector.Generator(fd_r)
		)

	@property
	def BytesPerSector(self):
		return 2 ** self['BytesPerSectorShift']

	@property
	def SectorsPerCluster(self):
		return 2 ** self['SectorsPerClusterShift']

	def write(self, fd_w):
		for name, offset, size in Bootsector.FIELDS:
			fd_w.seek(offset)
			fd_w.write(
				size.revert(self[name])
			)

		fd_w.seek(0)
		region = fd_w.read(11 * self.BytesPerSector)

		checksum = 0
		for i, byte in enumerate(region):
			if i in (106, 107, 112):
				continue

			checksum = (0x80000000 if checksum & 1 else 0) + (checksum >> 1) + byte

		data_checksum = Conversion.u32.revert(checksum) * (self.BytesPerSector // 4)

		fd_w.write(data_checksum)

		fd_w.write(region)
		fd_w.write(data_checksum)

