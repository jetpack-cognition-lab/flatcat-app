"""flatcat-app/updater

updaterlib used by updater-cl (command line) and updater_api (flask API)
"""
import argparse
import os, sys, re
import string
import random
import requests
import logging

from datetime import datetime
from clint.textui import progress
from subprocess import run, CalledProcessError, PIPE

# http = urllib3.PoolManager()

# import urllib
# urllib.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

from config import (
    base_home,
    base_hostname,
    base_local,
    base_url,
    base_work
)

from flatcat.logging import create_logger

VERBOSE = True

logger = create_logger('updaterlib', 'info')

def ns2kw(ns):
    """ns2kw

    utility func to convert argparse namespace to dictionary
    """
    kw = dict([(_, getattr(ns, _)) for _ in dir(ns) if not _.startswith('_')])
    return kw

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
    """get_list_remote

    Get the list of available updates from remote
    """
    if call_url is None:
        call_url = base_url
    logger.info(f'get_list_remote {call_url}')
    r = requests.get(call_url)
    # TODO: this is the raw html, parse that or get .txt file listing
    list_of_updates = r.text.strip()
    list_of_updates = re.sub(r'<html>.+</h1><hr><pre>(.*)</pre><hr></body>\r\n</html>', r'\1', list_of_updates, count=0, flags=re.M | re.S)
    list_of_updates = [re.sub(r'<a href="(.*)">.*', r'\1', _) for _ in list_of_updates.split('\r\n') if len(_) > 0]
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

def get_download_url(install_version):
    if install_version == 'current':
        current_file, current_version = get_current_remote()
    else:
        if install_version.startswith('flatcat-') and install_version.endswith('.ar'):
            current_version = install_version.replace(".tar.bz2", "").replace(".ar", "").replace("flatcat-", "")
            current_file = install_version
        else:
            current_version = install_version
            current_file = f'flatcat-{current_version}.tar.bz2'
    return current_file, current_version

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
    return {
        'location': location,
        'total_length': total_length,
    }

def run_command(command, hot=False):
    if VERBOSE:
        logger.info(f'run_command = {" ".join(command)}')
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

# main functions: download, install
def updater_download(*args, **kwargs):
    """updater_download

    Download install_version from repository and store locally
    """
    current_file, current_version = get_download_url(kwargs['install_version'])
    call_url = base_url + '/' + current_file
    logger.info(f'call_url = {call_url}')
    call_location = f'{base_work}/{current_file}'
    logger.info(f'call_location = {call_location}')
    res_download = download_from_url_into_file(call_url, call_location)
    return {
        'current_version': current_version,
        'current_file': current_file,
        'url': call_url,
        'total_length': res_download['total_length'],
        'location': res_download['location'],
    }

def updater_install(*args, **kwargs):
    """updater_install

    Install the package install_version into the filesystem
    """
    commands = []
    # application stop
    # tmux kill-session -t flatcat
    cmd_line = ['tmux', 'kill-session', '-t', 'flatcat']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    timestamp = create_timestamp()
    # application backup
    if kwargs['install_backup']:
        # tar jcvf flatcat-20211020.tar.bz2 jetpack/
        # tar jcvf /home/pi/data/flatcat-name-20211029.tar.bz2 /home/pi/jetpack/
        hostname = socket.gethostname()
        filename = f'{hostname}-{timestamp}-local.tar.bz2'
        cmd_line = ['tar', 'jcvf', f'{base_work}/{filename}', base_local]
        cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
        commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # # move old dir out of the way
    # base_local_old = f'{base_work}/jetpack-backup-{timestamp}'
    # cmd_line = ['mv', '-v', base_local, base_local_old]
    # cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])

    # application unpack
    # tar jxvf data/flatcat-20211020.tar.bz2
    # filename = f'flatcat-20211020.tar.bz2'
    if kwargs['install_version'] == 'current':
        _, kwargs['install_version'] = get_current_remote() # "20211020"

    # unpack top-level archive
    filename = f"flatcat-{kwargs['install_version']}.ar"
    # cmd_line = ['ar', 'x', '--output', f'{HOME}/data/', f'{HOME}/data/{filename}']
    cmd_line = ['ar', 'x', f'{base_work}/{filename}']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # unpack control tar
    filename = f"flatcat-{kwargs['install_version']}-control.tar.bz2"
    cmd_line = ['mv', filename, f'{base_work}/']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])    
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    cmd_line = ['tar', 'jxvf', f'{base_work}/{filename}', '-C', f'{base_home}']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # run pre-install script
    cmd_line = ['python', f'{base_local}/flatcat-app/updater/updater-pre.py']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # unpack data tar
    filename = f"flatcat-{kwargs['install_version']}-data.tar.bz2"
    cmd_line = ['mv', filename, f'{base_work}/']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])    
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    cmd_line = ['tar', 'jxvf', f'{base_work}/{filename}', '-C', f'{base_home}']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # run post-install script
    # install crontab
    cmd_line = ['python', f'{base_local}/flatcat-app/updater/updater-post.py']
    # '--backup', base_local_old]
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})
    
    # application restart
    # /home/pi/jetpack/bootscripts/starttmux.sh
    # /home/pi/jetpack/setup/boot/start-tmux.sh
    cmd_line = [f'{base_local}/flatcat-setup/boot/start-tmux.sh']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})
    
    return {
        'commands': commands
    }
