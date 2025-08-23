from bootsector import Bootsector
from fat import Fat
from structure import Structure
from shift import calculate, Shift
from bitmap import Bitmap
from alter import alter
from argparse import ArgumentParser

def main():
	parser = ArgumentParser('exfatresize')

	parser.add_argument(
		'path', type = str, help = 'path to partition image or block device (e.g. /dev/sda1)'
	)
	parser.add_argument(
		'size', type = int, help = 'target partition size (in sectors)'
	)

	args = parser.parse_args()


	fd = open(args.path, 'rb+')

	print('Reading bootsector...')

	bootsector = Bootsector.create(fd)

	if bootsector['FileSystemName'] != 2314885754712905797:
		raise Exception('Opened file does not contain ExFAT filesystem!')

	if bootsector['NumberOfFats'] != 1:
		raise Exception('TexFAT is not supported.')

	print('Calculating cluster count...')

	calculations = calculate(args.size, bootsector)

	print('Reading FAT...')

	fat = Fat.create(fd, bootsector)

	print('Reading directory entries recursively...')

	structure = Structure.create(fd, bootsector, fat)

	print('Calculating clusters shift...')

	shift, zeroes = Shift(bootsector, calculations, fat, structure)

	print('Generating new allocation bitmap...')

	bitmap = Bitmap.create(bootsector, calculations, structure, zeroes)

	print('Generating new FAT...')

	fat.update(calculations, structure, shift)

	print('Altering data on partition...')

	alter(fd, args.size, bootsector, fat, structure, calculations, shift, bitmap)

	print('Done!')

if __name__ == '__main__':
	main()

