"""flatcat-app/updater

updaterlib
"""
import argparse
import os, sys
import string
import random
import requests
import logging

from datetime import datetime
from clint.textui import progress
from subprocess import run, CalledProcessError, PIPE

from config import (
    base_url,
    base_hostname,
    base_home,
    base_local,
    base_work
)

from flatcat.logging import create_logger

VERBOSE = True

logger = create_logger('updaterlib', 'info')

def updater_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='flatcat-app/updater command help', dest='mode')
    subparser_uuid = subparsers.add_parser('uuid', help='create new uuid help')
    
    subparser_list = subparsers.add_parser('list', help='Get list of update files help')

    subparser_current = subparsers.add_parser('current', help='Get current update file help')

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

    return parser
    
def create_uuid(k=4):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=k))

def create_directories():
    # directories = ['jetpack', 'data', 'work']
    directories = ['jetpack', 'work']
    for directory in directories:
        directory_path = f'{base_home}/{directory}'
        if not os.path.exists(directory_path):
            if VERBOSE:
                logger.info(f'creating directory {directory_path}')
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

def get_list_remote(call_url=None):
    if call_url is None:
        call_url = base_url
    logger.info(f'getting = {call_url}')
    r = requests.get(call_url)
    # TODO: this is the raw html, parse that or get .txt file listing
    list_of_updates = r.text.strip()
    logger.info(f'list_of_updates {list_of_updates}')
    # logger.info(f"new {current_version > args.installed_version}")
    return list_of_updates

def get_current_remote(call_url=None):
    if call_url is None:
        call_url = base_url + '/current.txt'
    logger.info(f'getting = {call_url}')
    r = requests.get(call_url)
    current_file = r.text.strip()
    current_version = current_file.replace(".tar.bz2", "").replace(".ar", "").replace("flatcat-", "")
    logger.info(f'current_file = {current_file}, current_version = {current_version}')
    # logger.info(f"new {current_version > args.installed_version}")
    return current_file, current_version

# def get_current_remote_2():
#     call_url = base_url + '/current.txt'
#     logger.info(f'getting = {call_url}')
#     r = http.request(
#         'GET',
#         call_url,
#         headers=headers,
#     )
#     current_file = r.data.decode().strip()
#     current_version = current_file.replace(".tar.bz2", "").replace(".ar", "").replace("flatcat-", "")
#     logger.info(f'current_file = {current_file}, current_version = {current_version}')
#     # logger.info(f"new {current_version > args.installed_version}")
#     return current_file, current_version

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
        logger.info(f'run_command command = {" ".join(command)}')
    success = True
    result_ = None
    if hot:
        try:
            result = run(command, stdout=PIPE, check=True)
            result_ = result.stdout.decode('utf-8')
            logger.info(f'{result_}')
        except (CalledProcessError, FileNotFoundError) as e:
            success = False
            logger.error(f'error {e}')
    else:
        logger.info(f'dry run')
    # result.stdout.decode('utf-8')
    return success, result_

