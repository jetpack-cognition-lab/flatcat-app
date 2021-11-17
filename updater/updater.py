"""flatcat-app/updater

# user
- check for new update
- download update
- install update

# admin (factor out eventually?)
- package new update from local build
- upload new update from new package
"""
import sys
import os
import urllib3
import requests
import shutil
import argparse
import json
import time
import os
import socket
import random
import string


from pprint import pformat
from clint.textui import progress
from subprocess import run, CalledProcessError
from datetime import datetime

http = urllib3.PoolManager()

# import urllib
# urllib.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

headers = {}

HOME = os.environ['HOME']
VERBOSE = True

from config import (
    base_url,
    base_hostname
)

def create_uuid(k=4):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=k))

def create_directories():
    directories = ['jetpack', 'data', 'work']
    for directory in directories:
        directory_path = f'{HOME}/{directory}'
        if not os.path.exists(directory_path):
            if VERBOSE:
                print(f'creating directory {directory_path}')
            os.mkdir(directory_path)

def create_timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S')

def is_running():
    """flatcat app is running
    """
    pass

# def download2():
#     resp = requests.get('http://www.mywebsite.com/user')
#     resp = requests.post('http://www.mywebsite.com/user')
#     resp = requests.put('http://www.mywebsite.com/user/put')
#     resp = requests.delete('http://www.mywebsite.com/user/delete')

def download_from_url_into_file(url, location):
    # with requests.get(url, stream=True) as r:
    #     with open(location, 'wb') as f:
    #         shutil.copyfileobj(r.raw, f)

    r = requests.get(url, stream=True)
    # path = '/some/path/for/file.txt'
    with open(location, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()
    return location

def run_command(command, hot=False):
    if VERBOSE:
        print(f'run_command command = {" ".join(command)}')
    success = True
    if hot:
        try:
            run(command, check=True)
        except (CalledProcessError, FileNotFoundError) as e:
            success = False
            print(f'error {e}')
    else:
        print(f'dry run')
    return success

def main_uuid(args):
    """main_uuid
    """
    uuid_instance = create_uuid(k=4)
    print(f"uuid = {uuid_instance}")
    return uuid_instance

def main_download(args):
    if args.install_version == 'current':
        call_url = base_url + '/current.txt'
        print(f'getting = {call_url}')
        r = http.request(
            'GET',
            call_url,
            headers=headers,
        )
        current_file = r.data.decode().strip()
        current_version = current_file.replace(".tar.bz2", "").replace("flatcat-", "")
        print(f'current_file = {current_file}, current_version = {current_version}')
        print(f"new {current_version > args.installed_version}")
    else:
        current_version = args.install_version
        current_file = f'flatcat-{current_version}.tar.bz2'
        
    call_url = base_url + '/' + current_file
    print(f'call_url = {call_url}')
    location = download_from_url_into_file(call_url, f'{HOME}/data/{current_file}')

def main_install(args):
    """main_install

    Install a downloaded package
    1. stop running app
    2. create backup of current version
    3. unpack new version
    4. test new version
    5. start new version
    6. clean up backup
    """
    # application stop
    # tmux kill-session -t flatcat
    command = ['tmux', 'kill-session', '-t', 'flatcat']
    run_command(command, args.run_hot)

    # application backup
    if args.install_backup:
        # tar jcvf flatcat-20211020.tar.bz2 jetpack/
        # tar jcvf /home/pi/data/flatcat-name-20211029.tar.bz2 /home/pi/jetpack/
        hostname = socket.gethostname()
        timestamp = create_timestamp()
        filename = f'{hostname}-{timestamp}-local.tar.bz2'
        command = ['tar', 'jcvf', f'{HOME}/data/{filename}', f'{HOME}/jetpack']
        run_command(command, args.run_hot)

    # move old dir out of the way
    # TODO
    command = ['mv', '-v', f'{HOME}/jetpack', f'{HOME}/jetpack-backup-{timestamp}']
    run_command(command, args.run_hot)

    # application unpack
    # tar jxvf data/flatcat-20211020.tar.bz2
    # filename = f'flatcat-20211020.tar.bz2'
    if args.install_version == 'current':
        args.install_version = "20211020"

    # unpack archive
    filename = f'flatcat-{args.install_version}.ar'
    command = ['ar', 'x', '--output', f'{HOME}/data/', f'{HOME}/data/{filename}']
    run_command(command, args.run_hot)
    
    filename = f'flatcat-{args.install_version}-control.tar.bz2'
    command = ['tar', 'jxvf', f'{HOME}/data/{filename}', '-C', '/']
    run_command(command, args.run_hot)
    
    command = ['python', f'{HOME}/jetpack/flatcat-app/updater/updater-pre.py']
    run_command(command, args.run_hot)

    filename = f'flatcat-{args.install_version}-data.tar.bz2'
    command = ['tar', 'jxvf', f'{HOME}/data/{filename}', '-C', '/']
    run_command(command, args.run_hot)

    # TODO
    # install crontab
    command = ['python', f'{HOME}/jetpack/flatcat-app/updater/updater-post.py']
    run_command(command, args.run_hot)
    
    # application restart
    # /home/pi/jetpack/bootscripts/starttmux.sh
    # /home/pi/jetpack/setup/boot/start-tmux.sh
    command = [f'{HOME}/jetpack/flatcat-setup/boot/start-tmux.sh']
    run_command(command, args.run_hot)
    return

def main_package(args):
    """package an update

    - list of files in package
    - runtime vs. sdk version
    - list of control files in package
    """
    print(f'main_package packaging new update')

    # package_list_runtime = [
    #     # flatcat main controller
    #     'flatcat-ux0/ux0_serial',
    #     'flatcat-ux0/flatcat.dat.dist',
    #     # flatcat-setup
    #     'flatcat-setup/readme.txt',
    #     'flatcat-setup/boot',
    #     'flatcat-setup/boot/start-tmux.sh',
    #     'flatcat-setup/boot/start-ap-managed-wifi.sh',
    #     'flatcat-setup/network',
    #     'flatcat-setup/network/hostapd.conf',
    #     'flatcat-setup/network/interfaces',
    #     'flatcat-setup/network/wpa_supplicant.conf',
    #     'flatcat-setup/crontabfile',
    # ]
    # print(f'package_list_runtime =\n{pformat(package_list_runtime)}')
    
    # # write list to file
    # with open('package_list_runtime.txt', 'w') as f:
    #     for item in package_list_runtime:
    #         f.write(f"{item}\n")
    
    # # read list from file
    # with open('flatcat-app/updater/package_list_runtime.txt', 'r') as f:
    #     l = [_.strip() for _ in f.readlines()] 
    #     print(l)

    # create full archive with data + control a la debian
    timestamp = create_timestamp()
    # tar command transforming the path with raspberry prefix, taking inputs from a file
    # package data
    package_data_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}-data.tar.bz2'
    package_data_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_data_file_name} -T flatcat-app/updater/data/package_list_runtime.txt'.split(' ')
    print(f'package_data_command = {package_data_command}')
    run_command(package_data_command, args.run_hot)

    # package control
    package_control_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}-control.tar.bz2'
    package_control_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_control_file_name} -T flatcat-app/updater/data/package_list_control.txt'.split(' ')
    print(f'package_control_command = {package_control_command}')
    run_command(package_control_command, args.run_hot)

    # package total
    package_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}.ar'
    package_command = f'ar q {package_file_name} {package_data_file_name} {package_control_file_name}'.split(' ')
    print(f'package_command = {package_command}')
    run_command(package_command, args.run_hot)

def main_upload(args):
    """upload a packaged update

    - upload the package file
    - update current.txt
    """
    update_filename = os.path.basename(args.filename)
    update_filename_path = f"flatcat-app/updater/data/{update_filename}"
    upload_command = f"scp {update_filename_path} {base_hostname}:/home/www/jetpack_base/flatcat/updates/".split(' ')
    print(f'upload_command = {upload_command}')
    uploaded = run_command(upload_command, args.run_hot)

    if not uploaded:
        print('main_upload upload failed')
        return

    update_current_command = ['ssh', 'base.jetpack.cl', f'echo {update_filename} >/home/www/jetpack_base/flatcat/updates/current.txt']
    run_command(update_current_command, args.run_hot)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='flatcat-app/updater command help', dest='mode')
    subparser_uuid = subparsers.add_parser('uuid', help='create new uuid help')
    
    subparser_download = subparsers.add_parser('download', help='download update file help')
    subparser_download.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    
    subparser_install = subparsers.add_parser('install', help='install update file help')
    subparser_install.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    subparser_install.add_argument("-b", "--backup", dest='install_backup', action='store_true', default=False, help="Create tar.bz2 backup of current install [False]")
    subparser_install.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    subparser_package = subparsers.add_parser('package', help='package an update help')
    subparser_package.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")
    subparser_package.add_argument("-s", "--sdk", dest='package_version', help="Install full runtime or full sdk [runtime]", default = 'runtime')

    subparser_upload = subparsers.add_parser('upload', help='upload an update help')
    subparser_upload.add_argument("-f", "--filename", dest='filename', help="Which filename to upload [flatcat-20211117-171041.tar.bz2]", default = 'flatcat-20211117-171041.tar.bz2')
    subparser_upload.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    args = parser.parse_args()
    args.installed_version = '20211001'
    # 20211202
    print(f'__main__ args = {args}')

    # check directories / initialize
    create_directories()
    
    if args.mode == 'download':
        _main = main_download
    elif args.mode == 'install':
        _main = main_install
    elif args.mode == 'uuid':
        _main = main_uuid
    elif args.mode == 'package':
        _main = main_package
    elif args.mode == 'upload':
        _main = main_upload
    else:
        print('Unknown mode {0}, exiting'.format(args.mode))
        sys.exit(1)

    ret = _main(args)
    print(f'__main__ return {ret}')
