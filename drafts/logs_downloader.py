#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import os
import zipfile
import tarfile
import argparse
from urllib.parse import urlparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog="logs_downloader", description="Download logs from web url"
    )
    parser.add_argument(
                "url",
                type=str,
                help="url to images artifacts data",
            )
    parser.add_argument(
                "--path",
                type=str,
                default="/tmp",
                help=("Base path to download logs to")
            )
    return parser.parse_args()


args = parse_args()
base_url = args.url

if base_url.endswith('/'):
    base_url = url[:-1]

base_path = urlparse(base_url).path.split('/')[:-1]
base_len = len(base_path)

def get_nested_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html5lib')
    relative_links = soup.findAll('a')
    # there can be some links lokking like <a href="../">../</a>, filter out them
    # and construct full links from relative links
    links = [url + link['href'] for link in relative_links if '../' not in link['href']]
    res = []
    for l in links:
        if l.endswith('/'):
            #print("Found Dir! {}".format(l))
            res.extend(get_nested_links(l))
        else:
            #print("Found File! {}".format(l))
            res.append(l)
    return res

def download_url(url, path):
    print(f"Started downloading {url}")
    chunk_size = 100
    response = requests.get(url)
    with open(path, 'wb') as fd:
        for chunk in response.iter_content(chunk_size):
            fd.write(chunk)

all_links = get_nested_links(base_url + "/")

for l in all_links:
    path = urlparse(l).path
    f_name = os.path.basename(path)


    tpath = '/'.join(path.split('/')[base_len:])
    tdir = os.path.dirname(tpath)
    tdir_path = f"{args.path}/{tdir}"

    if not os.path.exists(tdir_path):
         os.makedirs(tdir_path)

    log_file_path = "%s/%s" % (tdir_path,f_name)

    download_url(l, log_file_path)

    remove_src = False
    if f_name.endswith('.zip'):
        with zipfile.ZipFile(log_file_path,"r") as zip_ref:
            zip_ref.extractall(f"{tdir_path}/")
        remove_src = True
    if f_name.endswith('.tar.gz'):
        with tarfile.open(log_file_path,"r") as tar_ref:
            tar_ref.extractall(f"{tdir_path}/")
        remove_src = True
    if remove_src:
        os.remove(log_file_path)
