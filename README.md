# PythonRsync
Python Program For Remote Directory Comparison

1. Introduction

Rsync is a fast and extraordinarily versatile file copying tool. It can copy locally, to/from another host over any remote shell, or to/from a remote rsync daemon. It offers a large number of options that control every aspect of its behavior and permit very flexible specification of the set of files to be copied. It is famous for its delta-transfer algorithm, which reduces the amount of data sent over the network by sending only the differences between the source files and the existing files in the destination. Rsync is widely used for backups and mirroring and as an improved copy command for everyday use. 

The main purpose of the project is to write a code that displays a formatted output of differing files (both local and remote) that are obtained by using rsync command. Following are the three main functions of the code:
1. Displays the files that differ in both local and remote
2. Displays the files that are common in both local and remote along with their timestamps
3. Create scripts to copy files to and fro from local and remote

In all the three cases that are mentioned above, files are not copied instead they are just displayed on the screen. Scripts are created, which can be later used to sync local and remote files.

The code is entirely written in python using the default libraries that come along with python installation. 


2. Requirements

Following are the prerequisites to make the code working

1. Python ( v2.7 to v3.4)
2. Configure the machines to accept the SSH connections



3. How To Execute

1. Copy the dirs-compare.py to a folder  and give executable permissions
	chmod +x dirs-compare.py

2. Execute the code according to the usage
	usage: dirs-compare.py [-h] [-f] [-s SCRIPTDIRECTORY] Directory1 Directory2


4. Arguments

Following are the description of the arguments that need to be passed to the code while execution:

Positional arguments:
	  Directory1 - Origin Directory
	  Directory2 - Destination Directory(Can be local or remote. If remote then the 					format that needs to be given is Username@Hostname:DirectoryPath)

Note: If the remote directory is not mentioned, then the local directory path is considered as the remote path. For example, 
	./dirs-compare –fast /home/testdir test@remotehost

In this case remote directory path is also considered as /home/testdir
		
Optional arguments:
  -h, --help
	show this help message and exit

  -f, --fast
	Compare files only by size instead of by checksum. By default, rsync compares files via checksums, but this can be slow with large files. The --fast option will cause file to be compared only by size--i.e., files will be considered identical if they are the same size.

  -s SCRIPTDIRECTORY, 	--scriptdirectory SCRIPTDIRECTORY
	Local directory for saving merging scripts. If SCRIPTS_DIRECTORY is supplied, two scripts will be written there:
	(1) mergeonly.sh -- Script to copy files that occur in only one argument directory
		                            to the other argument directory, resulting in no "missing" files.
	(2) mergediff.sh -- Script to copy the newest of any files that differ between the
		                           two argument directories to the other directory, overwriting
		                           the older file.
	Thus, after executing both scripts, the two argument directories will be identical.


5. Sample Output

 Directories:
 --------------------------------------
 D1: /home/tux/handouts
 D2: test@remotehost:/home/tux/handouts
 
 Files in Only One Directory:
  D1  D2  File
   --- ---  ------------------------------
  X       commands/commands.text.old
  X       files [directory]
  X       functions/functions.ps
      X   functions/functions.text.save1
  X       init/init.pdf.save1
  X       init/init.tex.save1
      X   installation/installation.tex~
      X   installation/installation.toc
      X   ssh/ssh.tex~
      X   sudo/slides.pdf
      X   sudo/slides.tex
      X   sudo/slides.tex~
  X       sudo/susudo.tex~
 --- ---
   6   7
 
 Differing files: (7)
 ----------------------------------------
 commands/commands.ps.gz:
      9941  2013-08-12 12:06 *         9741  2013-06-12 12:44
 functions/functions.pdf:
      8173  2011-02-11 09:55           8223  2012-01-09 13:25 *
 functions/functions.text:
     16945  2011-02-11 09:55          16965  2012-01-09 13:24 *
 init/init.pdf:
     94492  2013-07-09 16:27 *        93559  2013-07-08 13:08
 init/init.tex:
     24861  2013-07-09 16:27 *        24537  2013-07-08 13:08
 installation/installation.pdf:
    228040  2013-06-06 18:03         232826  2013-07-03 16:38 *

