#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import os
import zipfile
import tarfile
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('url', help='url to get logs from')
args = parser.parse_args()
url = args.url

cluster_name = url.split('/')[-2]
logs_path = '/tmp/%s' % (cluster_name)

r = requests.get(url)
soup = BeautifulSoup(r.content,'html5lib')
links = soup.findAll('a')

node_links = [url + link['href'] for link in links if '../' not in link['href']]
nodes = {}

#print node_links

for l in node_links:
#    print l
    lk = BeautifulSoup(requests.get(l).content,'html5lib').findAll('a')
#    print lk
    nodes[l.split('/')[-2]] = [l + link['href'] for link in lk if not '../' in link['href']]

if not os.path.exists(logs_path):
    os.makedirs(logs_path)

for n,links in nodes.iteritems():
    node_logs_path = "%s/%s" % (logs_path,n)
    if not os.path.exists(node_logs_path):
        os.makedirs(node_logs_path)
#    print links
    for l in links:
        f_name = l.split('/')[-1]
        log = requests.get(l)
        log_name = "%s/%s" % (node_logs_path,f_name) 
        with open (log_name, 'w') as f:
            f.write(log.content)
        if f_name.endswith('.zip'):
            with zipfile.ZipFile(log_name,"r") as zip_ref:
                zip_ref.extractall("%s/" % str(node_logs_path))
        if f_name.endswith('.tar.gz'):
            with tarfile.open(log_name,"r") as tar_ref:
                tar_ref.extractall("%s/" % str(node_logs_path))
        os.remove(log_name)

