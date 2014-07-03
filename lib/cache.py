import sublime

import json
import os
import time

def get_cache_path():
    return sublime.packages_path() + '/User/cdnjs.packages.cache'


def time_has_passed(last_time, time_now):
    time_is_blank = time_now is None or last_time is None
    if time_is_blank:
        return time_is_blank
    time_difference = int(time.time()) - int(last_time)
    time_has_passed = time_difference > int(time_now)

    return time_has_passed


def get_package_list(path):
    packageList = ''
    with open(path, 'r') as f:
        packageList = f.read()
    return packageList


def set_package_list(path, packageList):
    with open(path, 'w') as f:
        f.write(packageList)


def optimize_cache(data):
    data = json.loads(data)

    for p in data['packages']:
        # delete unused keys
        for key in list(p):
            if key not in ['assets', 'name', 'description']:
                del p[key]

        # simplify assets data structure
        assets = {}
        for i, a in enumerate(p['assets']):
            files = []
            for f in a['files']:
                files.append(f['name'])
            assets[a['version']] = files
        p['assets'] = assets

    return json.dumps(data)
