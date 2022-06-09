#!/usr/bin/env python
import argparse
import yaml
import json
from urllib import request

def parse_args():
    parser = argparse.ArgumentParser(
        prog="hack-os-ctl", description="Create hacks for os ctl"
    )
    parser.add_argument(
                "--artifacts-url",
                type=str,
                help="url to images artifacts data",
            )
    parser.add_argument("osctl_path", help=("Path to os ctl code"))
    parser.add_argument(
                "--patch",
                type=bool,
                default=False,
                help="Boolean. Whether to make patch to ctl",
            )
    return parser.parse_args()


def main():
    args = parse_args()

    with request.urlopen(args.artifacts_url) as httpObj:
        tgt_imgs = yaml.safe_load(httpObj)
    os_version =[key for key in tgt_imgs.keys()][0]

    template_path = f"{args.osctl_path}/templates/{os_version}/artifacts.yaml"

    with open(template_path, "r") as template_obj:
        template_dict = yaml.safe_load(template_obj)

    tags = {}
    for key, val in template_dict.items():
        component = val.split('/')[-1].split(':')[0]
        if component in tgt_imgs[os_version].keys():
            tags[key] = tgt_imgs[os_version][component]["url"]
    extra_context = {"openstack":{"spec":{"common":{"openstack":{"values":{"images":{"tags":tags}}}}}}}
    output = json.dumps(extra_context)
    print(output)
    if args.patch:
        with open(template_path, "w") as template_obj:
            for key in tags.keys():
                template_dict[key] = tags[key]
            yaml.dump(template_dict, template_obj)

if __name__ == "__main__":
    main()
