#!/usr/bin/env python

from pygerrit.ssh import GerritSSHClient
import json
from pprint import pprint
import time

import datetime

start = (2018,11,15)
end = (2018,12,15)

d_start = datetime.date(start[0],start[1],start[2])
d_end = datetime.date(end[0],end[1],end[2])

ut_start = time.mktime(d_start.timetuple())
ut_end = time.mktime(d_end.timetuple())

print d_start
print d_end

print ut_start
print ut_end

client = GerritSSHClient("review")

x = 0

#projects = ['nova']
projects=['nova','cinder','glance','keystone','horizon','neutron','designate','heat','ironic','barbican', 'aodh', 'ceilometer', 'gnocchi', 'panko', 'manila', 'salt', 'linux', 'reclass', 'galera', 'memcached', 'rabbitmq', 'bind', 'apache', 'runtest', 'oslo-templates', 'auditd', 'octavia', 'openscap']

for i in projects:
    cmd = "query --patch-sets --format=JSON project:salt-formulas/{} after:{} before:{}".format(i,d_start,d_end)
    #print cmd
    result = client.run_gerrit_command(cmd)
    lst = result.stdout.read().rstrip().split('\n')
    for c in lst:
        change = json.loads(c)
        patchSets = change.get('patchSets')
        if patchSets:
            for p in patchSets:
                if p['createdOn'] >= ut_start and p['createdOn'] <= ut_end:
                    x += 1
print x
