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

# http = urllib3.PoolManager()

# import urllib
# urllib.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

headers = {}

HOME = os.environ['HOME']
VERBOSE = True

from config import (
    base_url,
    base_hostname,
    base_home,
    base_local,
    base_work
)

from flatcat.common import (
    create_uuid,
    create_directories,
    create_timestamp,
    is_running,
    download_from_url_into_file,
    get_current_remote,
    run_command,
    updater_parser
)

from flatcat.logging import create_logger

logger = create_logger(sys.argv[0], 'info')

def get_current_local():
    pass

def main_uuid(args):
    """main_uuid
    """
    uuid_instance = create_uuid(k=4)
    logger.info(f"uuid = {uuid_instance}")
    return uuid_instance

def main_download(args):
    if args.install_version == 'current':
        current_file, current_version = get_current_remote()
    else:
        current_version = args.install_version
        current_file = f'flatcat-{current_version}.tar.bz2'
        
    call_url = base_url + '/' + current_file
    logger.info(f'call_url = {call_url}')
    location = download_from_url_into_file(call_url, f'{base_work}/{current_file}')

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

    timestamp = create_timestamp()
    # application backup
    if args.install_backup:
        # tar jcvf flatcat-20211020.tar.bz2 jetpack/
        # tar jcvf /home/pi/data/flatcat-name-20211029.tar.bz2 /home/pi/jetpack/
        hostname = socket.gethostname()
        filename = f'{hostname}-{timestamp}-local.tar.bz2'
        command = ['tar', 'jcvf', f'{base_work}/{filename}', base_local]
        run_command(command, args.run_hot)

    # # move old dir out of the way
    # base_local_old = f'{base_work}/jetpack-backup-{timestamp}'
    # command = ['mv', '-v', base_local, base_local_old]
    # run_command(command, args.run_hot)

    # application unpack
    # tar jxvf data/flatcat-20211020.tar.bz2
    # filename = f'flatcat-20211020.tar.bz2'
    if args.install_version == 'current':
        _, args.install_version  = get_current_remote() # "20211020"

    # unpack top-level archive
    filename = f'flatcat-{args.install_version}.ar'
    # command = ['ar', 'x', '--output', f'{HOME}/data/', f'{HOME}/data/{filename}']
    command = ['ar', 'x', f'{base_work}/{filename}']
    run_command(command, args.run_hot)

    # unpck control tar
    filename = f'flatcat-{args.install_version}-control.tar.bz2'
    command = ['mv', filename, f'{base_work}/']
    run_command(command, args.run_hot)    
    command = ['tar', 'jxvf', f'{base_work}/{filename}', '-C', f'{base_home}']
    run_command(command, args.run_hot)

    # run pre-install script
    command = ['python', f'{base_local}/flatcat-app/updater/updater-pre.py']
    run_command(command, args.run_hot)

    # unpack data tar
    filename = f'flatcat-{args.install_version}-data.tar.bz2'
    command = ['mv', filename, f'{base_work}/']
    run_command(command, args.run_hot)    
    command = ['tar', 'jxvf', f'{base_work}/{filename}', '-C', f'{base_home}']
    run_command(command, args.run_hot)

    # run post-install script
    # install crontab
    command = ['python', f'{base_local}/flatcat-app/updater/updater-post.py']
    # '--backup', base_local_old]
    run_command(command, args.run_hot)
    
    # application restart
    # /home/pi/jetpack/bootscripts/starttmux.sh
    # /home/pi/jetpack/setup/boot/start-tmux.sh
    command = [f'{base_local}/flatcat-setup/boot/start-tmux.sh']
    run_command(command, args.run_hot)
    return

def main_package(args):
    """package an update

    - list of files in package
    - runtime vs. sdk version
    - list of control files in package
    """
    logger.info(f'main_package packaging new update')

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
    # logger.info(f'package_list_runtime =\n{pformat(package_list_runtime)}')
    
    # # write list to file
    # with open('package_list_runtime.txt', 'w') as f:
    #     for item in package_list_runtime:
    #         f.write(f"{item}\n")
    
    # # read list from file
    # with open('flatcat-app/updater/package_list_runtime.txt', 'r') as f:
    #     l = [_.strip() for _ in f.readlines()] 
    #     logger.info(l)

    # create full archive with data + control a la debian
    timestamp = create_timestamp()

    # tar command transforming the path with raspberry prefix, taking inputs from a file
    # package data
    package_data_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}-data.tar.bz2'
    # package_data_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_data_file_name} -T flatcat-app/updater/data/package_list_runtime.txt'.split(' ')
    package_data_command = f'tar --transform s/^flatcat-/jetpack\/flatcat-/ -jcf {package_data_file_name} -T flatcat-app/updater/data/package_list_runtime.txt'.split(' ')
    logger.info(f'package_data_command = {package_data_command}')
    run_command(package_data_command, args.run_hot)

    # package control
    package_control_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}-control.tar.bz2'
    # package_control_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_control_file_name} -T flatcat-app/updater/data/package_list_control.txt'.split(' ')
    package_control_command = f'tar --transform s/^flatcat-/jetpack\/flatcat-/ -jcf {package_control_file_name} -T flatcat-app/updater/data/package_list_control.txt'.split(' ')
    logger.info(f'package_control_command = {package_control_command}')
    run_command(package_control_command, args.run_hot)

    # package total
    package_file_name = f'flatcat-app/updater/data/flatcat-{timestamp}.ar'
    package_command = f'ar q {package_file_name} {package_data_file_name} {package_control_file_name}'.split(' ')
    logger.info(f'package_command = {package_command}')
    run_command(package_command, args.run_hot)

def main_upload(args):
    """upload a packaged update

    - upload the package file
    - update current.txt
    """
    update_filename = os.path.basename(args.filename)
    update_filename_path = f"flatcat-app/updater/data/{update_filename}"
    upload_command = f"scp {update_filename_path} {base_hostname}:/home/www/jetpack_base/flatcat/updates/".split(' ')
    logger.info(f'upload_command = {upload_command}')
    uploaded = run_command(upload_command, args.run_hot)

    if not uploaded:
        logger.info('main_upload upload failed')
        return

    update_current_command = ['ssh', 'base.jetpack.cl', f'echo {update_filename} >/home/www/jetpack_base/flatcat/updates/current.txt']
    run_command(update_current_command, args.run_hot)
    
if __name__ == '__main__':
    parser = updater_parser()
    args = parser.parse_args()
    args.installed_version = '20211001'
    # 20211202
    logger.info(f'__main__ args = {args}')

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
        logger.info('Unknown mode {0}, exiting'.format(args.mode))
        sys.exit(1)

    ret = _main(args)
    logger.info(f'__main__ return {ret}')
