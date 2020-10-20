#!/usr/bin/env python3

##########################################################################################
# Copyright (c) 2020 Nordic Semiconductor ASA. All Rights Reserved.
#
# The information contained herein is confidential property of Nordic Semiconductor ASA.
# The use, copying, transfer or disclosure of such information is prohibited except by
# express written agreement with Nordic Semiconductor ASA.
##########################################################################################

import os
import zipfile
import glob
import subprocess
import shutil
import yaml
import time
import datetime
import urllib.request
import concurrent.futures
from tabulate import tabulate
    
BUILD_FOLDER = "_build"
VERSION = "none"
DATE = datetime.datetime.now().strftime("%Y-%m-%d")
SHA = '0'*40
SHORT_SHA = '0'*8

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'target_configs.yaml')) as f:
    CONFIGS = yaml.full_load(f)

def create_folder(folder: str) -> None:
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

def build_target(name: str, data: dict) -> str:
    build_folder = os.path.join(BUILD_FOLDER, name + '-' + data['platform'])
    create_folder(build_folder)
    cmd = f"cmake -GNinja -DBOARD={data['platform']} -H{data['path']} -B{build_folder}".split()
    if 'configuration' in data:
        cmd.extend(data['configuration']['extra_configs'])

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    assert proc.returncode == 0, f"Command:{proc.args}\nReturncode: {proc.returncode}\nOutput:\n{proc.stdout.decode()}\n"
    cmd = "ninja".split()
    proc = subprocess.run(
        cmd,
        cwd=build_folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    assert proc.returncode == 0, f"Command:{proc.args}\nReturncode: {proc.returncode}\nOutput:\n{proc.stdout.decode()}\n"
    return build_folder

def scan_artifacts(data: dict, build_folder: str) -> dict:
    release_files = list()
    for k, v in CONFIGS['files'].items():
        a = glob.glob(build_folder+v['pattern'])
        if not a:
            print(f"WARN: Not found glob: {build_folder+v['pattern']}")
            continue
        arcname = v['prefix'] 
        if data['configuration']['extra_path']:
            arcname += '/'.join(data['configuration']['extra_path']) + '/'
        arcname += data['filename']
        if data['configuration']['extra_names']:
            arcname += '_' + '_'.join(data['configuration']['extra_names'])
        arcname += v['postfix']
        desc = data['description']
        if data['configuration']['extra_desc']:
            desc += ", " + ", ".join(data['configuration']['extra_desc'])
        release_files.append(
            (a[0], arcname.format(**globals()), desc)
        )
    return release_files

def handle_target(name: str, data: dict) -> dict:
    print(f"  Building: {name}...")
    build_folder = build_target(name, data)
    return scan_artifacts(data, build_folder)

def config_constructor(loader, node) -> dict:
    config = loader.construct_sequence(node)
    ret = {
        'extra_configs': [],
        'extra_names': [],
        'extra_desc': [],
        'extra_path': []
    }
    for i in config:
        if 'cmake_configs' in CONFIGS['configs'][i]:
            ret['extra_configs'].extend(["-D" + x for x in CONFIGS['configs'][i]['cmake_configs']])
        if 'extra_name' in CONFIGS['configs'][i]:
            ret['extra_names'].append(CONFIGS['configs'][i]['extra_name'])
        if 'extra_path' in CONFIGS['configs'][i]:
            ret['extra_path'].append(CONFIGS['configs'][i]['extra_path'])
        if 'extra_desc' in CONFIGS['configs'][i]:
            ret['extra_desc'].append(CONFIGS['configs'][i]['extra_desc'])
    return ret

def main(release_desc: str, single_target: str) -> None:
    global VERSION
    global SHA
    global SHORT_SHA

    create_folder(BUILD_FOLDER)
    start = time.time()
    print("Create Release")
    yaml.add_constructor("!config", config_constructor)
    with open(release_desc, "rb") as f:
        data = yaml.full_load(f.read())

    if 'version_folder' in data:
        VERSION = subprocess.check_output(
            ['git', 'describe'], 
            cwd=data['version_folder']
        ).decode().strip()
        SHA = subprocess.check_output(
            ['git', 'rev-parse', '--verify', 'HEAD'],
            cwd=data['version_folder']
        ).decode().strip()
        SHORT_SHA = SHA[0:8]
    
    if single_target:
        for target in data['targets']:
            for k, v in target.items():
                if k == single_target:
                    handle_target(single_target, v)
                    print("Completed")
                    return
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_results = list()
            for target in data['targets']:
                future_results.extend(
                    [executor.submit(handle_target, k, v) for k, v in target.items()]
                )
        concurrent.futures.wait(future_results)
    print("Build completed, creating zip...")

    release_name = data['release_name'].format(**globals())
    print("Name: ", release_name)

    filelist = list()
    zipname = os.path.join("outcomes", release_name)
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as z:
        for future in future_results:
            for file_path, archive_path, desc in future.result():
                print(f"Writing {file_path} as {archive_path}...")
                z.write(file_path, archive_path)
                filelist.append([archive_path, desc])

        if 'external_files' in data:
            for _, context in data['external_files'].items():
                name = context['url'].rsplit('/', 1)[-1]
                with urllib.request.urlopen(context['url']) as response:
                    z.writestr(name, response.read())
                filelist.append([name, context['description']])

        filelist.sort()
        release_contents = tabulate(filelist, headers=["File", "Description"])
        for name, context in data['generated_files'].items():
            readme = context['text'].format(**globals(), release_contents=release_contents)
            z.writestr(context['name'], readme.replace('\n', '\r\n'))
                        
    print(f"Completed {time.time() - start}s")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('release_description_file')
    parser.add_argument('--target', help="Name of single target")
    args = parser.parse_args()
    root = os.path.dirname(__file__)
    manifest = os.path.join(root, f"target_{args.release_description_file}.yaml")
    main(manifest, args.target)
