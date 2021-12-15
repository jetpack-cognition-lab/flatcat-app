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

headers = {}
headers_json = {'Content-Type': 'application/json'}

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
    get_download_url,
    run_command,
    ns2kw,
    updater_parser,
    updater_download,
    updater_install,
    update_version_tag,
    get_version_tag,
    configuration_get_wifi,
    flatcat_live,
    get_current_local,
)

from flatcat.logging import create_logger

logger = create_logger(sys.argv[0], 'info')

def main_uuid(args):
    """main_uuid
    """
    uuid_instance = create_uuid(k=4)
    logger.info(f"uuid = {uuid_instance}")
    return uuid_instance

def main_download(args):
    """main_download

    Download `install_version` from repository and store locally
    """
    return updater_download(**(ns2kw(args)))

def main_install(args):
    """main_install

    Install a downloaded package
    """
    return updater_install(**(ns2kw(args)))
    
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
    # with open('{dir_flatcatapp}/updater/package_list_runtime.txt', 'r') as f:
    #     l = [_.strip() for _ in f.readlines()] 
    #     logger.info(l)

    # create full archive with data + control a la debian
    timestamp = create_timestamp()
    kwargs = ns2kw(args)

    # update version tag from timestamp
    update_version_tag(os.getcwd(), timestamp)
    
    # tar command transforming the path with raspberry prefix, taking inputs from a file
    # package data
    package_data_file_name = f'{dir_flatcatapp}/updater/data/flatcat-{timestamp}-data.tar.bz2'
    # package_data_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_data_file_name} -T {dir_flatcatapp}/updater/data/package_list_runtime.txt'.split(' ')
    package_data_command = f'tar --transform s/^flatcat-/jetpack\/flatcat-/ -jcf {package_data_file_name} -T {dir_flatcatapp}/updater/data/package_list_runtime.txt'.split(' ')
    logger.info(f'package_data_command = {package_data_command}')
    cmd_status, cmd_output = run_command(package_data_command, kwargs['run_hot'])
    if not cmd_status:
        logger.error(f'package_data_command failed, stopping')
        return
    
    # package control
    package_control_file_name = f'{dir_flatcatapp}/updater/data/flatcat-{timestamp}-control.tar.bz2'
    # package_control_command = f'tar --transform s/^flatcat-/home\/pi\/jetpack\/flatcat-/ -jcf {package_control_file_name} -T {dir_flatcatapp}/updater/data/package_list_control.txt'.split(' ')
    package_control_command = f'tar --transform s/^flatcat-/jetpack\/flatcat-/ -jcf {package_control_file_name} -T {dir_flatcatapp}/updater/data/package_list_control.txt'.split(' ')
    logger.info(f'package_control_command = {package_control_command}')
    cmd_status, cmd_output = run_command(package_control_command, kwargs['run_hot'])
    if not cmd_status:
        logger.error(f'package_data_command failed, stopping')
        return

    # package total
    package_file_name = f'{dir_flatcatapp}/updater/data/flatcat-{timestamp}.ar'
    package_command = f'ar q {package_file_name} {package_data_file_name} {package_control_file_name}'.split(' ')
    logger.info(f'package_command = {package_command}')
    cmd_status, cmd_output = run_command(package_command, kwargs['run_hot'])
    if not cmd_status:
        logger.error(f'package_data_command failed, stopping')
        return

def main_upload(args):
    """upload a packaged update

    - upload the package file
    - update current.txt
    """
    kwargs = ns2kw(args)

    update_datadir = '{dir_flatcatapp}/updater/data'
    if kwargs['filename'] is None:
        update_filename, update_version = get_current_local(update_datadir)
    else:
        update_filename = kwargs['filename']
    update_filename = os.path.basename(update_filename)

    update_filename_path = f"{update_datadir}/{update_filename}"
    upload_command = f"scp {update_filename_path} {base_hostname}:/home/www/jetpack_base/flatcat/updates/".split(' ')
    logger.info(f'main_upload: upload_command = {upload_command}')
    uploaded = run_command(upload_command, kwargs['run_hot'])

    if not uploaded[0]:
        logger.error('main_upload: upload failed')
        return False

    update_current_command = ['ssh', 'base.jetpack.cl', f'echo {update_filename} >/home/www/jetpack_base/flatcat/updates/current.txt']
    run_command(update_current_command, kwargs['run_hot'])

def main_configure_wpa(args):
    """configure_wpa a packaged update

    - configure_wpa the package file
    - update current.txt
    """
    kwargs = ns2kw(args)
    configuration_get_wifi(**kwargs)

def main_test_flatcat_live(args):
    """flatcat_live a packaged update

    - flatcat_live the package file
    - update current.txt
    """
    kwargs = ns2kw(args)
    ret = flatcat_live(**kwargs)
    return ret

def main_test_rewrite_flatcatdat(args):
    """main_test_rewrite_flatcatdat

    Test rewrite flatcat.dat.dist to flatcat.dat
    """
    kwargs = ns2kw(args)
    ret = rewrite_flatcatdat(**kwargs)
    return ret

if __name__ == '__main__':
    parser = updater_parser()
    args = parser.parse_args()
    # TODO: get local versioning sorted
    # args.installed_version = '20211001'
    args.installed_version = get_version_tag(os.getcwd())
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
    elif args.mode == 'configure_wpa':
        _main = main_configure_wpa
    elif args.mode == 'test_flatcat_live':
        _main = main_test_flatcat_live
    elif args.mode == 'test_rewrite_flatcatdat':
        _main = main_test_rewrite_flatcatdat
    else:
        logger.info('Unknown mode {0}, exiting'.format(args.mode))
        sys.exit(1)

    ret = _main(args)
    logger.info(f'__main__ return {ret}')
