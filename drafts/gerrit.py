#!/usr/bin/env python
from __future__ import division
from pygerrit.ssh import GerritSSHClient
import json
from pprint import pprint
import time
from datetime import timedelta, date
from collections import OrderedDict
#import matplotlib.pyplot as plt
from operator import itemgetter
import argparse

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--start', help='start of the period in format yyyy-mm-dd')
parser.add_argument('--end', help='end of the period in format yyyy-mm-dd')
parser.add_argument('--max', action="store_true", default=False , help='Show day with maximum number of patch sets overall projects')
parser.add_argument('--per-project', action="store_true", dest='per_project', default=False , help='Show statistics per each project')

args = parser.parse_args()

start = [int(i) for i in args.start.split('-')]
end = [int(i) for i in args.end.split('-')]

d_start = date(start[0],start[1],start[2])
d_end = date(end[0],end[1],end[2])

client = GerritSSHClient("review")

openstack_projects = ['nova','cinder','glance','keystone','horizon','neutron','designate','heat','ironic','barbican', 'aodh', 'ceilometer', 'gnocchi', 'panko', 'manila', 'salt', 'linux', 'reclass', 'galera', 'memcached', 'rabbitmq', 'bind', 'apache', 'runtest', 'oslo-templates', 'auditd', 'octavia', 'openscap']
openstack_salt_formulas = ['salt-formulas/{}'.format(i) for i in openstack_projects]
pkg_projects = ['^packaging/specs/.*']
aio_model = ['salt-models/mcp-virtual-aio']
model_projects = ['mk/cookiecutter-templates','salt-models/reclass-system']
projects = openstack_salt_formulas + pkg_projects + model_projects + aio_model
#projects = ['salt-formulas/nova']

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

stat0 = """

Statistics about patch sets overall projects for the period:
"""

print stat0

# Patch sets per day over all projects
stats_days = OrderedDict()
period_sum = 0
pfpd = 0
mpd = 0
ppd = 0
fpd = 0
pf_ds = 0
m_ds = 0
p_ds = 0
f_ds = 0
cpd = 0
c_ds = 0
rpd = 0
r_ds = 0
for d in days:
    stats_days[d] = 0
    for p in projects:
        if stats[p][d] > 0:
            if p in openstack_salt_formulas or p == 'salt-models/mcp-virtual-aio':
                pfpd += 1
                pf_ds += stats[p][d]
            if p in openstack_salt_formulas:
                fpd += 1
                f_ds += stats[p][d]
            if p in pkg_projects:
                ppd += 1
                p_ds += stats[p][d]
            if p == 'mk/cookiecutter-templates':
                cpd += 1
                c_ds += stats[p][d]
            if p == 'salt-models/reclass-system':
                rpd += 1
                r_ds += stats[p][d]
            else:
                mpd += 1
                m_ds += stats[p][d]
        stats_days[d] += stats[p][d]
    period_sum += stats_days[d]
    print '    Day {} - patch_sets {}'.format(d,stats_days[d])
print '    Total in ALL projects {} - {} is {}'.format(d_start,d_end,period_sum)

if pf_ds > 0:
    print '    Total in formulas + mcp-virtual-aio {}'.format(pf_ds)
    print '    Mean per day in formulas + mcp-virtual-aio {}'.format(pf_ds / pfpd)
if f_ds > 0:
    print '    Total in formulas {}'.format(f_ds)
    print '    Mean per day in formulas {}'.format(f_ds / fpd)
if p_ds > 0:
    print '    Total in packages {}'.format(p_ds)
    print '    Mean per day in packages {}'.format(p_ds / ppd)
if c_ds > 0:
    print '    Total in cookiecutter-templates {}'.format(c_ds)
    print '    Mean per day in cookiecutter-templates {}'.format(c_ds / cpd)
if r_ds > 0:
    print '    Total in reclass-system {}'.format(r_ds)
    print '    Mean per day in reclass-system {}'.format(r_ds / cpd)
if m_ds > 0:
    print '    Total in reclass-system + cookiecutter-templates projects {}'.format(m_ds)
    print '    Mean per day in reclass-system + cookiecutter-templates projects {}'.format(m_ds / mpd)


if args.per_project:
    stat1 = """

Statistics about patch sets per project for the period:
"""

    print stat1

    # Patch sets per project
    for i in projects:
        print 'Project {}:'.format(i)
        days_sum = 0
        patch_days = 0
        for d in days:
            days_sum += stats[i][d]
            if stats[i][d] > 0:
                patch_days += 1
                print '    {} - patch_sets {}'.format(d,stats[i][d])
        if days_sum > 0:
            mean = days_sum / patch_days
            print '    Total patch_sets {}'.format(days_sum)
            print '    Mean per day {}'.format(mean)
        else:
            print '    No patch_sets found for the period'


if args.max:
    stat2 = """

Statistics about day with higest number of patchsets overall projects:
"""

    print stat2


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
            print '    {} - {} - patch_sets {}'.format(i,d,stats[i][d])



#plt.plot(stats.keys(),stats.values())
#plt.show()