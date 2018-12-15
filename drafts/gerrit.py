#!/usr/bin/env python

from pygerrit.ssh import GerritSSHClient
import json
from pprint import pprint
import time
from datetime import timedelta, date
from collections import OrderedDict
import matplotlib.pyplot as plt
from operator import itemgetter

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start = (2018,12,11)
end = (2018,12,15)

d_start = date(start[0],start[1],start[2])
d_end = date(end[0],end[1],end[2])

print d_start
print d_end

client = GerritSSHClient("review")

#projects = ['nova']
openstack_projects = ['nova','cinder','glance','keystone','horizon','neutron','designate','heat','ironic','barbican', 'aodh', 'ceilometer', 'gnocchi', 'panko', 'manila', 'salt', 'linux', 'reclass', 'galera', 'memcached', 'rabbitmq', 'bind', 'apache', 'runtest', 'oslo-templates', 'auditd', 'octavia', 'openscap']
openstack_salt_formulas = ['salt-formulas/{}'.format(i) for i in openstack_projects]
pkg_projects = ['^packaging/specs/.*']
model_projects = ['mk/cookiecutter-templates','salt-models/reclass-system']
projects = openstack_salt_formulas + pkg_projects + model_projects
data = {}
stats = {}
days = []


for i in projects:
    cmd = "query --patch-sets --format=JSON project:{} after:{}".format(i,d_start)
    result = client.run_gerrit_command(cmd)
    data[i] = [json.loads(change) for change in result.stdout.read().rstrip().split('\n')]
    stats[i] = OrderedDict()

for d in daterange(d_start, d_end):
    day = d.strftime("%Y-%m-%d")
    days.append(day)
    ut_start = time.mktime(d.timetuple())
    ut_end = time.mktime((d+timedelta(days=1)).timetuple())
    for k,v in data.items():
        stats[k][day] = 0
        for change in v:
            if change.get('patchSets'):
                for p in change['patchSets']:
                    if p['createdOn'] >= ut_start and p['createdOn'] <= ut_end:
                        stats[k][day] += 1

# Patch sets per day over all projects
stats_days = OrderedDict()
period_sum = 0
for d in days:
    stats_days[d] = 0
    for project,s in stats.items():
        stats_days[d] += s[d]
    period_sum += stats_days[d]
    print 'Day {} - patch_sets {}'.format(d,stats_days[d])
print 'Number of patch_sets for period {} - {} is {}'.format(d_start,d_end,period_sum)

# Patch sets per project
for i in projects:
    print 'Project {}:'.format(i)
    days_sum = 0
    for d in days:
        days_sum += stats[i][d]
        if stats[i][d] > 0:
            print '    {} - patch_sets {}'.format(d,stats[i][d])
    if days_sum > 0:
        print '    Period patch_sets {}'.format(days_sum)
    else:
        print 'No patch_sets found for the period'


# Find days with the highest number of patch sets
# and check in which project it was
x = sorted(stats_days.items(), key=itemgetter(1))
max_ps = x[-1][1]
max_days = []
for i in x:
    if max_ps in i:
        max_days.append(i[0])
for i in projects:
    for d in max_days:
        print '{} - {} - patch_sets {}'.format(i,d,stats[i][d])



#plt.plot(stats.keys(),stats.values())
#plt.show()