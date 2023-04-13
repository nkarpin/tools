#!/usr/bin/env python

import argparse
from bs4 import BeautifulSoup
import logging
import os
import requests
import subprocess
import tarfile
import tempfile
import time
import zipfile

from urllib.parse import urlparse

logger = logging.getLogger("logs_downloader")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

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

def run_cmd(popenargs,
            return_stdout=False,
            return_stderr=False,
            check=True,
            timeout=None,
            **kwargs):
    """Run subprocess and write output to tmp files"""
    def _get_output(out_file, return_out=False):
        out = []
        out_file.seek(0)
        for line in out_file:
            l = line.decode().strip()
            logger.info(l)
            if return_out:
                out.append(l)
        return out
    out = []
    err = []
    with tempfile.NamedTemporaryFile(delete=True) as errf:
        with tempfile.NamedTemporaryFile(delete=True) as outf:
            try:
                logger.info(f"Running command: {popenargs}, started at {time.ctime(time.time())}")
                child = subprocess.run(popenargs, stdout=outf, stderr=errf, timeout=timeout, check=check, **kwargs)
                logger.info(f"Finished command: {popenargs} at {time.ctime(time.time())}")
                res = child.returncode
            finally:
                logger.info("Command STDOUT:")
                out = _get_output(outf, return_stdout)
                logger.info("Command STDERR:")
                err = _get_output(errf, return_stderr)
    return (res, out, err)

def run_tar_extract(archive, path):
    try:
        run_cmd(["tar", "-C", path, "-xvf", archive], check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Got exception {e} while running tar")

args = parse_args()
base_url = args.url

if base_url.endswith('/'):
    base_url = base_url[:-1]

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

print(all_links)

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
        run_tar_extract(log_file_path, f"{tdir_path}/")
        remove_src = True
    if remove_src:
        os.remove(log_file_path)
