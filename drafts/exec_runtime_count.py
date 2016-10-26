#!/usr/bin/python

import sys
import re

from collections import defaultdict

strace_lines = open(sys.argv[1]).readlines()

lines = filter(lambda l:'execve(\"' in l or 'exited' in l, strace_lines)
lines = sorted(lines, key=lambda l: l.split()[0])

pid_lines=defaultdict(list)

process_info={}

for line in lines:
	pid_time_proc = line.split(' ',1)
	#print pid_time_proc
	pid=line.split()[0]
	#print pid
	if pid in line:
	 	pid_lines[pid].append(pid_time_proc[1])

#print pid_lines

for pid in pid_lines.keys():
	if len(pid_lines[pid]) == 2:
#		print pid_lines[pid][1]
#		print pid_lines[pid][0]
		proc_runtime = float(pid_lines[pid][1].split()[0]) - float(pid_lines[pid][0].split()[0])
		process_info[pid] = [pid_lines[pid][0],pid_lines[pid][1],proc_runtime*1000]

tmp=[]

for pid in process_info.keys():
	print process_info[pid]
	proc_name = process_info[pid][0].split(' ',1)[1]
	proc_time = process_info[pid][2]
	tmp.append([pid,proc_name,proc_time])

tmp_sort=sorted(tmp, key=lambda l: l[2])

for i in tmp_sort:
	print "pid: %s name: %s runtime: %s" % (i[0],i[1],i[2])

