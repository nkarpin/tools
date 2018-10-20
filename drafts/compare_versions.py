#!/usr/bin/env python

from deb_pkg_tools.control import deb822_from_string,parse_control_fields
from deb_pkg_tools.version import Version
import requests
import gzip
import sys
import tempfile

def get_packages_versions(parsed):
    packages = {}
    for i in parsed:
        if i['Package'] in packages.keys():
            packages[i['Package']].append(i['Version'])
        else:
            packages[i['Package']] = [i['Version']]
    return packages

def get_packages_gz(url):
    obj = tempfile.NamedTemporaryFile(prefix='tmpPackagesGZ', dir='/tmp', delete=False)
    gz = requests.get("%s/Packages.gz" % (url))
    with open(obj.name, 'wb') as f:
        f.write(gz.content)
    return obj.name

def parse_packages_gz(file):
    fields = []
    s = gzip.open(file, 'rb').read()
    for i in s.strip().split('\n\n'):
        fields.append(parse_control_fields(deb822_from_string(i)))
    return fields

def get_versions_diff(packages1, packages2, repo1, repo2):
    diff = {}
    print("Comparing repo1 - %s and repo2 - %s" % (repo1,repo2))
    pkgs = set(packages1.keys()).intersection(packages2.keys())
    for k in pkgs:
        # TODO: Get difference by highest version
        # sorted1 = (sorted(Version(s) for s in packages1[k]))
        # sorted2 = (sorted(Version(s) for s in packages1[k]))

        # Get overall defference
        repo1_pkg_diff = set(packages1[k]) - set(packages2[k])
        repo2_pkg_diff = set(packages2[k]) - set(packages1[k])
        if repo1_pkg_diff or repo2_pkg_diff:
            diff[k] = {}
        if repo1_pkg_diff:
            diff[k].update({'repo1': repo1_pkg_diff})
        if repo2_pkg_diff:
            diff[k].update({'repo2': repo2_pkg_diff})
    return diff

dist_version = sys.argv[1]
os_version = sys.argv[2]
mcp_rev = sys.argv[3]

repo1 = 'http://mirror.mirantis.com/%s/openstack-%s/%s/dists/%s/main/binary-amd64' % (mcp_rev,os_version,dist_version,dist_version)
repo2 = 'http://apt.mirantis.com/%s/openstack/%s/dists/%s/main/binary-amd64' % (dist_version,os_version,mcp_rev)

# repo1 = 'http://mirror.mirantis.com/nightly/salt-formulas/xenial/dists/xenial/main/binary-amd64'
# repo2 = 'http://apt.mirantis.com/xenial/dists/testing/salt/binary-amd64'

file1 = get_packages_gz(repo1)
file2 = get_packages_gz(repo2)

parsed_pkgs_fields1 = parse_packages_gz(file1)
parsed_pkgs_fields2 = parse_packages_gz(file2)

packages1 = get_packages_versions(parsed_pkgs_fields1)
packages2 = get_packages_versions(parsed_pkgs_fields2)

repo1_diff = set(packages1.keys()) - set(packages2.keys())
repo2_diff = set(packages2.keys()) - set(packages1.keys())

if repo1_diff:
    print("Repo 2 has no packages: %s" % (repo1_diff))

if repo2_diff:
    print("Repo 1 has no packages: %s" % (repo2_diff))

diff = get_versions_diff(packages1, packages2, repo1, repo2)

if diff:
    for k,v in diff.iteritems():
        print("Package %s have next versions %s" % (k,v))
else:
    print("All packages and version are the same")