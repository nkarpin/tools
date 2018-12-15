#!/usr/bin/env python

from pygerrit.ssh import GerritSSHClient
import json
from pprint import pprint
import time
from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start = (2018,12,01)
end = (2018,12,15)

d_start = date(start[0],start[1],start[2])
d_end = date(end[0],end[1],end[2])

print d_start
print d_end

client = GerritSSHClient("review")

#projects = ['nova']
projects=['nova','cinder','glance','keystone','horizon','neutron','designate','heat','ironic','barbican', 'aodh', 'ceilometer', 'gnocchi', 'panko', 'manila', 'salt', 'linux', 'reclass', 'galera', 'memcached', 'rabbitmq', 'bind', 'apache', 'runtest', 'oslo-templates', 'auditd', 'octavia', 'openscap']
data = {}
stats = {'sum_patch_sets': 0}



for i in projects:
    cmd = "query --patch-sets --format=JSON project:salt-formulas/{} after:{} before:{}".format(i,d_start,d_end)
    result = client.run_gerrit_command(cmd)
    data[i] = [json.loads(change) for change in result.stdout.read().rstrip().split('\n')]
    stats[i] = {'sum_patch_sets': 0}


for d in daterange(d_start, d_end):
    day = d.strftime("%Y-%m-%d")
    ut_start = time.mktime(d.timetuple())
    ut_end = time.mktime((d+timedelta(days=1)).timetuple())
    for k,v in data.items():
        stats[k][day] = {}
        stats[k][day]['patch_sets'] = 0
        for change in v:
            if change.get('patchSets'):
                for p in change['patchSets']:
                    if p['createdOn'] >= ut_start and p['createdOn'] <= ut_end:
                        stats[k][day]['patch_sets'] += 1
        stats[k]['sum_patch_sets'] += stats[k][day]['patch_sets']

for k,v in data.items():
    print stats[k]['sum_patch_sets']
    stats['sum_patch_sets'] += stats[k]['sum_patch_sets']

print stats['sum_patch_sets']