#!/usr/bin/python

# sysctl max_pid should be increased because pids are used as identifiers
# for execs

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

#for key in sorted(pid_lines.keys()):
#	print key,pid_lines[key]


#print pid_lines

for pid in pid_lines.keys():
	if len(pid_lines[pid]) == 2:
#		print pid_lines[pid][1]
#		print pid_lines[pid][0]
#			if 'exited' in pid_lines[pid]:
#		print pid,pid_lines[pid]
		if 'exited' not in pid_lines[pid][0] or 'exited' not in pid_lines[pid][1]:
			proc_runtime = float(pid_lines[pid][1].split()[0]) - float(pid_lines[pid][0].split()[0])
			process_info[pid] = [pid_lines[pid][0],pid_lines[pid][1],proc_runtime*1000]
#			print pid,pid_lines[pid]
#	if len(pid_lines[pid]) > 2 and 'ifconfig' not in pid_lines[pid][0] and '/sbin/ip' not in pid_lines[pid][0]:
#		print pid,pid_lines[pid]

tmp=[]

for pid in process_info.keys():
#	print process_info[pid]
	proc_name = process_info[pid][0].split(' ',1)[1]
	proc_time = process_info[pid][2]
	tmp.append([pid,proc_name,proc_time])

tmp_sort=sorted(tmp, key=lambda l: l[2])

sum_time = 0

ifcfg_sum_time = 0
ifcfg_num = 0

iplnk_sum_time = 0
iplnk_num = 0

sgdisk_sum_time = 0
sgdisk_num = 0

lsbrelease_sum_time = 0
lsbrelease_num = 0

aptdpkg_sum_time = 0
aptdpkg_num = 0

grepcatawk_sum_time = 0
grepcatawk_num = 0

netstatarp_sum_time = 0
netstatarp_num = 0

virtwhat_sum_time = 0
virtwhat_num = 0


for i in tmp_sort:
#	print "pid: %s name: %s runtime: %s \n" % (i[0],i[1].strip(),i[2])
	if 'puppet' not in i[1] and 'apply' not in i[1] and 'osnaily' not in [1]:
		sum_time += float(i[2])
#		print i[0], i[1]
	if '\"/sbin/ifconfig ' in i[1]:
		ifcfg_sum_time += float(i[2])
		ifcfg_num +=1
	if '/sbin/ip' in i[1]:
		iplnk_sum_time += float(i[2])
		iplnk_num += 1
	if 'sgdisk ' in i[1]:
		sgdisk_sum_time += float(i[2])
		sgdisk_num += 1
	if '/usr/bin/lsb_release ' in i[1]:
		lsbrelease_sum_time += float(i[2])
		lsbrelease_num += 1
	if 'apt' in i[1] or 'dpkg' in i[1]:
		aptdpkg_sum_time += float(i[2])
		aptdpkg_num +=1
	if 'grep' in i[1] or '/bin/cat ' in i[1] or 'awk' in i[1]:
		grepcatawk_sum_time += float(i[2])
		grepcatawk_num += 1
	if '/bin/netstat' in i[1] or 'arp' in i[1]:
		netstatarp_sum_time += float(i[2])
		netstatarp_num += 1
	if '/usr/sbin/virt-what ' in i[1]:
		virtwhat_sum_time += float(i[2])
		virtwhat_num += 1

#	else:
#		print i

print "Full exec runtime: %s" % sum_time

print "Full ifconfig exec runtime: %s times: %s" % (ifcfg_sum_time, ifcfg_num)

print "Full ip link show exec runtime: %s times: %s" % (iplnk_sum_time, iplnk_num)

print "Full sgdisk exec runtime: %s times: %s" % (sgdisk_sum_time, sgdisk_num)

print "Full /usr/bin/lsb_release exec runtime: %s times: %s" % (lsbrelease_sum_time, lsbrelease_num)

print "Full apt and dpkg exec runtime: %s times: %s" % (aptdpkg_sum_time, aptdpkg_num)

print "Full grep cat awk exec runtime: %s times: %s" % (grepcatawk_sum_time, grepcatawk_num)

print "Full netstat and arp exec runtime: %s times: %s" % (netstatarp_sum_time, netstatarp_num)

print "Full virtwhat exec runtime: %s times: %s" % (virtwhat_sum_time, virtwhat_num)

