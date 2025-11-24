# exfatresize
This tool allows you to resize ExFAT partition in-place.
## This tool does only prepare the filesystem! You have to update partition scheme entry (e.g. with parted) manually!
### When you shrink the partition, you have use this tool first - then you update partition scheme.
### When you stretch the partition, you update partition scheme first!
## This utility has not been thoroughly tested!
### It seems to work well, when it has to update bootsector, FAT and allocation bitmap.
### Physically moving clusters while shrinking partition also passed correctly during the quick test.
### The edge-case, which I'm not sure about, is when the partition is stretched so much that the initial clusters need to be moved forward to make room for the much larger FAT
## If your partition contains important data, do not use this tool, or make a backup first!
