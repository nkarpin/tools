#!/usr/bin/python

from deb_pkg_tools.control import deb822_from_string,parse_control_fields
import requests
import gzip
import sys

dist_version = sys.argv[1]
os_version = sys.argv[2]
mcp_rev = sys.argv[3]

repo1 = 'http://mirror.mirantis.com/%s/openstack-%s/%s/dists/%s/main/binary-amd64' % (mcp_rev,os_version,dist_version,dist_version)
repo2 = 'http://apt.mirantis.com/%s/openstack/%s/dists/%s/main/binary-amd64' % (dist_version,os_version,mcp_rev)

pkgs_gz1 = requests.get("%s/Packages.gz" % (repo1))
pkgs_gz2 = requests.get("%s/Packages.gz" % (repo2))

file1 = '/tmp/packages_repo1.gz'
file2 = '/tmp/packages_repo2.gz'

with open(file2, 'wb') as f:  
    f.write(pkgs_gz2.content)

with open(file1, 'wb') as f:
    f.write(pkgs_gz1.content)

pkgs_str1 = gzip.open(file1, 'rb').read()
pkgs_str2 = gzip.open(file2, 'rb').read()

parsed_pkgs_fields1 = []
parsed_pkgs_fields2 = []


for i in pkgs_str1.split('\n\n'):
    parsed_pkgs_fields1.append(parse_control_fields(deb822_from_string(i)))


for i in pkgs_str2.split('\n\n'):
    parsed_pkgs_fields2.append(parse_control_fields(deb822_from_string(i)))

packages1 = {}
packages2 = {}

for i in parsed_pkgs_fields1:
    if i.get('Package'):
        if i['Package'] in packages1.keys():
            packages1[i['Package']].append(i['Version'])
        else:
            packages1[i['Package']] = [i['Version']]
    else:
        print("No 'Package' field in package %s in repo %s" % (i,repo1))

for i in parsed_pkgs_fields2:
    if i.get('Package'):
        if i['Package'] in packages2.keys():
            packages2[i['Package']].append(i['Version'])
        else:
            packages2[i['Package']] = [i['Version']]
    else:
        print("No 'Package' field in package %s in repo %s" % (i,repo2))


if len(packages1.keys()) != len(packages2.keys()):
    print('Repositories have different lists of packages')
    #print('Repo1 pkgs list %s')

#print packages1
diff = {}

for k,v in packages1.iteritems():
    if packages2.get(k):
        for i in v:
            if i not in packages2[k]:
                if diff.get(k, {}):
                    if diff[k].get(repo1):
                        diff[k][repo1].append(i)
                    else:
                        diff[k].update({repo1:[i]})
                else:
                    diff[k] = {repo1:[i]}
    else:
        print("Repo %s has no package %s " % (repo2,k))

for k,v in packages2.iteritems():
    if packages1.get(k):
        for i in v:
            if i not in packages1[k]:
                if diff.get(k, {}):
                    if diff[k].get(repo2):
                        diff[k][repo2].append(i)
                    else:
                        diff[k].update({repo2:[i]})
                else:
                    diff[k] = {repo2:[i]}
    else:
        print("Repo %s has no package %s " % (repo1,k))

if diff:
    for k,v in diff.iteritems():
        print("Package %s have next versions %s" % (k,v))
else:
    print("All packages and version are the same")


