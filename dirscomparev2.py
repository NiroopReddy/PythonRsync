#!/usr/bin/python2.7
#Author @Niroop Reddy Gade
#Works for Python version 2.7

import os
import subprocess
import argparse
from time import strptime

#Function to get list of files from directories and store it as dictionary {'filepath' : 'size and timestamp'}
#Eg: {'Documents/compare.py': '       12288 2015/11/29 02:19:57'}
#rsync -av has irrelevant information in lines 0 and 1 as well as the last 4 lines. So we remove them and store 
#the results in "output" 
def get_files(directory):
	proc = subprocess.Popen('rsync -av ' +  directory, 
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE,
		shell=True)
	output = proc.stdout.read().splitlines()[2:-4]
	files = {}
	for line in output:
		fields = line.split()
		fileinfo = fields[1] + ' ' + fields[2] + ' ' + fields[3]
		#print fileinfo
		if fields[0][0] != 'd':
			files[fields[4]] = fileinfo
		else:
			files[fields[4] + '[directory]'] = fileinfo
	return files

#Function to create unique dictionaries with local and remote file list obtained using above function.
#This function is used to separate files that are contained only in either local or remote directories.
def build_unique_dict(files1, files2):
	"""Returns dict with the keys of files1, files2 as keys. The values are:
		1 - if the key is only in files1
		2 - if the key is only in files2
		3 - if the key is in both files1 and files2"""
	unique = {} #Empty dictionary to store unique files
	
	#Loop to check if key exists in the dictionary and update its value accordingly
	for f in files1.keys():
		if f not in unique:
			unique[f] = 1
		else:
			unique[f] += 1

	for f in files2.keys():
		if f not in unique:
			unique[f] = 2
		else:
			unique[f] += 2

	return unique
	
#Function to print Files in only one directory
def print_unique_files(d):
	print "Files in Only One Directory:"
	print " D1  D2  File"
	print " --- ---  ------------------------------"
	keys = d.keys()
	keys = sorted(keys)	#Sort the keys in order of file structure
	num1 = 0
	num2 = 0
	for key in keys:
		if d[key]==1:
			print '  X' + ' '*8 + key
			num1 += 1
		elif d[key]==2:
			print ' '*6 + 'X' + ' '*4 + key
			num2 += 1	
	print " --- ---"
	print "{0:>3d}".format(num1) + ' ' + "{0:>3d}".format(num2) #Pad number with 0's(left padding, width 3)
	print

#Function to get files changed in the directories
def get_changed_files(directory1, directory2, isFast=False):
	if isFast:
		print "WARN: Using size-only fast file comparison. Not all changes may be detected."
		checking = '--size-only'
	else:
		checking = ''
	proc = subprocess.Popen('rsync -airnl --exclude=\"lost+found\" ' + checking + ' ' + directory1 + ' ' + directory2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = proc.stdout.read().splitlines()[:-1]
	#print output

	files = []
	for line in output:
		fields = line.split()
		#print fields
		if line[-1] != '/':
			files.append(fields[1])
		else:
			files.append(fields[1] + ' [directory]')
	return files

#Function to get changed files in both directories
def get_changed_files_in_both(unique, changed):
	files = []
	for f in changed:
		if f not in unique.keys():
			pass
		elif unique[f] == 3:
			files.append(f)
	return files


#Function to get the latest timestamp for the changed files
def fileinfo_compare(fi1, fi2):
	tim1 = fi1
	tim2 = fi2
	time1 = ' '.join(tim1.split()[1:])
	time2 = ' '.join(tim2.split()[1:])

	t1 = strptime(time1, "%Y/%m/%d %H:%M:%S")
	t2 = strptime(time2, "%Y/%m/%d %H:%M:%S")
	return t1 > t2
	
#Function to format and print changed files
def print_changed_files(changed, f1, f2):
	print "Differing files: ({})".format(len(changed))
	print "----------------------------------------"
	for f in sorted(changed):
		if fileinfo_compare(f1[f], f2[f]):
			f1_is_newer = '*'
			f2_is_newer = ' '
		else:
			f1_is_newer = ' '
			f2_is_newer = '*'

		print f + ':'
		#print ' '*8 + f1[f] + ' ' + f1_is_newer + ' ' + ' '*8 + f2[f] + ' ' + f2_is_newer
		print '{0:>35s} {1} {0:>35} {1}'.format(f1[f], f1_is_newer, f2[f], f2_is_newer)
	print

def create_update_scripts(outputdir, unique, changed, f1, f2, directory1, directory2):
	# Create script to copy unique files from directory1 to directory2 and back
	files_to_copy_to_f2 = []
	files_to_copy_from_f2 = []
	for f in unique:
		if "[directory]" in f:
			continue
		if unique[f] == 1:
			files_to_copy_to_f2.append(f + ' ')
		elif unique[f] == 2:
			files_to_copy_from_f2.append(f + ' ')

	mergeonly = '#!/bin/sh\n'
	for f in files_to_copy_to_f2:
		mergeonly += 'scp -p ' + directory1 + f + ' ' + directory2 + f + '\n'
	for f in files_to_copy_from_f2:
		mergeonly += 'scp -p ' + directory2 + f + ' ' + directory1 + f + '\n'


	mergediff = '#!/bin/sh\n'
	# Script to copy newly changed files from directory1 to directory2 and back
	files_to_copy_to_f2 = []
	files_to_copy_from_f2 = []
	for f in changed:
		if "[directory]" in f:
			continue
		# If directory 1 has the newer version of f
		if fileinfo_compare(f1[f], f2[f]):
			mergediff += 'scp -p ' + directory1 + f + ' ' + directory2 + f + '\n'
		else:
			mergediff += 'scp -p ' + directory2 + f + ' ' + directory1 + f + '\n'

	with open(os.path.abspath(outputdir) + '/mergeonly.sh', 'w') as f:
		f.write(mergeonly)

	with open(os.path.abspath(outputdir) + '/mergediff.sh', 'w') as f:
		f.write(mergediff)
	print "Saved mergeonly.sh and mergediff.sh to " + os.path.abspath(outputdir)
	print

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Rsync in python")
	parser.add_argument("Directory1", help="Origin Directory")
	parser.add_argument("Directory2", help="Destination Directory")
	parser.add_argument("-f", "--fast", action="store_true", help="Compare files only by size instead of by checksum")
	parser.add_argument("-s", "--scriptdirectory", help="Local directory for saving merging scripts")
	args = parser.parse_args()

	#Store the command line arguments to variables
	local_dir = args.Directory1
	#print local_dir
	remote_dir = args.Directory2
	#print remote_dir

	#Check for trailing backslashes in directory path and if not found add one
	if local_dir[-1] != '/':
		local_dir += '/'
	if remote_dir[-1] != '/':
		remote_dir += '/'
		
	local_files = get_files(local_dir) 			#Get list of files from local directory
	remote_files = get_files(remote_dir)			#Get list of files from remote directory
	unique = build_unique_dict(local_files, remote_files) 	#Build unique dictionary with files from local and remote
	print_unique_files(unique)				#Format and print files in only one directory
	files_changed = get_changed_files_in_both(unique, get_changed_files(local_dir, remote_dir, args.fast))	#Get files changed in both directories
	print_changed_files(files_changed, local_files, remote_files)	#Format and print files changed in both directories
	
	#Loop to create merge scripts using create_update_scripts function
	scriptdirectory = args.scriptdirectory
	if scriptdirectory is not None and len(scriptdirectory) > 0:
		if scriptdirectory[-1] != '/':
			scriptdirectory += '/'
		create_update_scripts(scriptdirectory, unique, files_changed, local_files, remote_files, local_dir, remote_dir)
