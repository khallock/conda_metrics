#!/usr/bin/env python
import argparse
from binstar_client.utils import get_server_api, spec
import binstar_client.errors

import sys

args = argparse.Namespace()
args.token = None
args.site = None
args.log_level = 0

packages = ['ncl', 'pynio', 'pyngl', 'wrf-python']
conda_channels = ['conda-forge', 'ncar', 'dbrown', 'khallock', 'bladwig']


if len(sys.argv) > 1:
    packages = sys.argv[1:]

for package in packages:
    package_total_dls = 0
    for conda_channel in conda_channels:
    #    s = spec.PackageSpec(conda_channel, package=package)

        aserver_api = get_server_api(args.token, args.site, args.log_level)
        try: package_obj = aserver_api.package(conda_channel, package)
        except binstar_client.errors.NotFound: continue
        channel_total_dls = 0
        for version_str in package_obj['versions']:
            version = aserver_api.release(conda_channel, package, version_str)
            for d in version['distributions']:
                #distribution_os = d['attrs']['operatingsystem']
                distribution_os = d['attrs']['machine']
                #distribution_arch = d['attrs']['arch']
                distribution_arch = d['attrs']['platform']
                distribution_build = d['attrs']['build']
                distribution_downloads = d['ndownloads']
                distribution_upload_time = d['upload_time']

                # detect numpy and python versions
                np_version = None
                py_version = None
                for item in d['dependencies']['depends']:
                    try:
                        if item['name'] == 'numpy':
                            np_version = item['specs'][0][1]
                        if item['name'] == 'python':
                            py_version = item['specs'][0][1]
                    except: pass
                #for key in d.keys():
                #    print "%s: %s" % (key, d[key])
                #sys.exit(0)
                print conda_channel, package, version_str, distribution_build, distribution_os, distribution_arch, distribution_downloads, py_version, np_version, distribution_upload_time
                channel_total_dls += distribution_downloads
        package_total_dls += channel_total_dls
        print "total downloads of", conda_channel, package, channel_total_dls
    print "total downloads of", package, package_total_dls
    print ""
