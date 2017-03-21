#!/usr/bin/env python
import argparse
from binstar_client.utils import get_server_api, spec
import binstar_client.errors

import sqlite3
import sys

# set up sqlite
conn = sqlite3.connect('conda_metrics.db')
c = conn.cursor()

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
        #db_table = "%s_%s" % (package, conda_channel)
        db_table = package.replace('-', '')

        aserver_api = get_server_api(args.token, args.site, args.log_level)
        try: package_obj = aserver_api.package(conda_channel, package)
        except binstar_client.errors.NotFound: continue
        try:
            c.execute('''CREATE TABLE %s (channel text, version text, build text, platform text, arch text, pyversion text, npversion text, uploaded_date date, downloads int, check_date datetime default CURRENT_TIMESTAMP)''' % db_table)
            conn.commit()
        except sqlite3.OperationalError:
            pass
        for version_str in package_obj['versions']:
            version = aserver_api.release(conda_channel, package, version_str)
            for d in version['distributions']:
                #distribution_os = d['attrs']['operatingsystem']
                distribution_os = d['attrs']['platform']
                #distribution_arch = d['attrs']['arch']
                distribution_arch = d['attrs']['machine']
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
                c.execute('''INSERT INTO %s (channel, version, build, platform, arch, pyversion, npversion, uploaded_date, downloads) VALUES (?,?,?,?,?,?,?,?,?)''' % db_table,
                             (conda_channel, version_str, distribution_build, distribution_os, distribution_arch, py_version, np_version, distribution_upload_time, distribution_downloads))
                conn.commit()
conn.close()
