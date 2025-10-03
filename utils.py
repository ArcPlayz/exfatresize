from struct import unpack, pack
from enum import Enum

class Conversion(Enum):
	u8 = (1, 'B')
	u16 = (2, 'H')
	u32 = (4, 'I')
	u64 = (8, 'Q')

	def __init__(self, size, code):
		self.size = size
		self.code = code

	def __call__(self, data, offset = 0):
		return unpack(
			'<' + self.code,
			data[offset:offset + self.size]
		)[0]

	def fd(self, fd_r):
		return self(fd_r.read(self.size))

	def revert(self, value):
		return pack('<' + self.code, value)

class ReturningGenerator:
	@staticmethod
	def create(generator_func):
		def generator_func_wrapped(*args, **kwargs):
			return ReturningGenerator(
				generator_func(*args, **kwargs)
			)

		return generator_func_wrapped

	def __init__(self, _generator):
		self.generator = _generator
		self.returned = None
		self.finished = False

	def __iter__(self):
		return self

	def __next__(self):
		try:	
			return next(self.generator)
		except StopIteration as ex:
			self.returned = ex.value
			self.finished = True

			raise

