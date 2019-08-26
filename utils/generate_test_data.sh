#!/bin/bash
#
# Script to generate dfVFS test files.
#
# Requires:
# * Linux
# * mkntfs

EXIT_SUCCESS=0;
EXIT_FAILURE=1;

set -e;

create_test_file_entries()
{
	MOUNT_POINT=$1;

	# Create a directory
	mkdir ${MOUNT_POINT}/a_directory;

	cat >${MOUNT_POINT}/a_directory/a_file <<EOT
This is a text file.

We should be able to parse it.
EOT

	cat >${MOUNT_POINT}/passwords.txt <<EOT
place,user,password
bank,joesmith,superrich
alarm system,-,1234
treasure chest,-,1111
uber secret laire,admin,admin
EOT

	cat >${MOUNT_POINT}/a_directory/another_file <<EOT
This is another file.
EOT

	ln -s ${MOUNT_POINT}/a_directory/another_file ${MOUNT_POINT}/a_link;
}

mkdir -p test_data;

MOUNT_POINT="/mnt/dfvfs";

sudo mkdir -p ${MOUNT_POINT};

# Create test image with an NTFS file system
IMAGE_NAME="ntfs.raw"
IMAGE_FILE="test_data/${IMAGE_NAME}";
IMAGE_SIZE=$(( 4096 * 1024 ));
SECTOR_SIZE=512;

dd if=/dev/zero of=${IMAGE_FILE} bs=${SECTOR_SIZE} count=$(( ${IMAGE_SIZE} / ${SECTOR_SIZE} )) 2> /dev/null;

mkntfs -F -q -L "ntfs_test" -s ${SECTOR_SIZE} ${IMAGE_FILE};

sudo mount -o loop,rw ${IMAGE_FILE} ${MOUNT_POINT};

create_test_file_entries ${MOUNT_POINT};

sudo umount ${MOUNT_POINT};

