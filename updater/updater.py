"""flatcat-app updater
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

from config import base_url

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
    print(f'run_command command = {" ".join(command)}')
    if hot:
        try:
            run(command, check=True)
        except (CalledProcessError, FileNotFoundError) as e:
            print(f'error {e}')
    else:
        print(f'dry run')

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
    # tar jcvf flatcat-20211020.tar.bz2 jetpack/
    # tar jcvf /home/pi/data/flatcat-name-20211029.tar.bz2 /home/pi/jetpack/
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f'{hostname}-{timestamp}-local.tar.bz2'
    command = ['tar', 'jcvf', f'{HOME}/data/{filename}', f'{HOME}/jetpack']
    run_command(command, args.run_hot)

    # move old dir out of the way
    # TODO
    command = ['mv', '-v', f'{HOME}/jetpack', f'{HOME}/jetpack-backup-{{timestamp}']
    run_command(command, args.run_hot)

    # application unpack
    # tar jxvf data/flatcat-20211020.tar.bz2
    # filename = f'flatcat-20211020.tar.bz2'
    if args.install_version == 'current':
        args.install_version = "20211020"
    filename = f'flatcat-{args.install_version}.tar.bz2'
    command = ['tar', 'jxvf', f'{HOME}/data/{filename}', '-C', '/']
    run_command(command, args.run_hot)

    # install crontab
    # TODO
    
    # application restart
    # /home/pi/jetpack/bootscripts/starttmux.sh
    command = [f'{HOME}/jetpack/bootscripts/starttmux.sh']
    run_command(command, args.run_hot)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='auto command help', dest='mode')
    subparser_download = subparsers.add_parser('download', help='download help')
    subparser_download.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    
    subparser_install = subparsers.add_parser('install', help='install help')
    subparser_install.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    subparser_install.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    subparser_uuid = subparsers.add_parser('uuid', help='uuid help')

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
    else:
        print('Unknown mode {0}, exiting'.format(args.mode))
        sys.exit(1)

    ret = _main(args)
    print(f'__main__ return {ret}')
