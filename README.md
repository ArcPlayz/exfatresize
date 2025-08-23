# exfatresize
This tool allows you to resize ExFAT partition in-place.
## This tool does only prepare the filesystem! You have to update partition scheme entry (e.g. with parted) manually!
### When you shrink the partition, you have use this tool first - then you update partition scheme.
### When you stretch the partition, you update partition scheme first!
## This utility has not been thoroughly tested!
### It seems to work well, when it has to update bootsector, FAT and allocation bitmap only. Is it safe, if it has to physically move clusters? I don't really know.
## If your partition contains important data, do not use this tool, or make a backup first!
This tool was created for Linux interoperability with Windows. NTFS sometimes happens to be problematic in that use-case.
