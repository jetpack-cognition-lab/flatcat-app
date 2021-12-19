"""flatcat_app/updater

updaterlib used by updater-cl (command line) and updater_api (flask API)
"""
import argparse
import os, sys, re
import string
import random
import requests
import logging
import json
import pprint
import tempfile

from pathlib import Path
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
    base_work,
    config_wpa_path,
    config_flatcat_path,
    dir_flatcatapp,
    dir_flatcatux0,
    dir_flatcatsetup,
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
        help=f'{dir_flatcatapp}/updater command help', dest='mode')
    subparser_uuid = subparsers.add_parser('uuid', help='create new uuid help')
    
    subparser_list = subparsers.add_parser('list', help='Get list of update files help')

    subparser_current = subparsers.add_parser('current', help='Get current update file help')

    subparser_download = subparsers.add_parser('download', help='download update file help')
    subparser_download.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    subparser_download.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")
    
    subparser_install = subparsers.add_parser('install', help='install update file help')
    subparser_install.add_argument("-i", "--install-version", dest='install_version', help="Which version to install [current]", default = 'current')
    subparser_install.add_argument("-b", "--backup", dest='install_backup', action='store_true', default=False, help="Create tar.bz2 backup of current install [False]")
    subparser_install.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    subparser_package = subparsers.add_parser('package', help='package an update help')
    subparser_package.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")
    subparser_package.add_argument("-s", "--sdk", dest='package_version', help="Install full runtime or full sdk [runtime]", default = 'runtime')

    subparser_upload = subparsers.add_parser('upload', help='upload an update help')
    subparser_upload.add_argument("-f", "--filename", dest='filename', help="Which filename to upload, if None use most recent [None]", default=None)
    subparser_upload.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    subparser_configure_wpa = subparsers.add_parser('configure_wpa', help='configure_wpa help')
    subparser_configure_wpa.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

    subparser_flatcat_live = subparsers.add_parser('flatcat_live', help='flatcat_live help')
    subparser_flatcat_live.add_argument("-r", "--run-hot", dest='run_hot', action='store_true', default=False, help="Really run commands [False]")

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

def update_version_tag(working_dir, version_string):
    version_file_path = f'{working_dir}/{dir_flatcatapp}/version.txt'
    bytes_written = 0
    with open(version_file_path, 'w') as f:
        bytes_written = f.write(version_string)
    return bytes_written

def get_version_tag(working_dir):
    version_file_path = f'{working_dir}/{dir_flatcatapp}/version.txt'
    logger.info(f'get_version_tag {version_file_path}')
    try:
        with open(version_file_path, 'r') as f:
            version_string = f.read().strip()
    except Exception as e:
        version_string = '0'
        
    return version_string

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

def get_current_local(update_datadir):
    logger.info(f'get_current_local: update_datadir {update_datadir}')
    folder_path = Path(update_datadir)
    list_of_paths = folder_path.glob('*')
    latest_path = max(list_of_paths, key=lambda p: p.stat().st_ctime)
    latest_path = str(latest_path)
    logger.info(f'get_current_local: latest_path {type(latest_path)}')
    latest_version = os.path.basename(latest_path.replace(".tar.bz2", "").replace(".ar", "").replace("flatcat-", ""))
    logger.info(f'get_current_local: {latest_path}, {latest_version}')
    return (latest_path, latest_version)

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
            current_file = f'flatcat-{current_version}.ar'
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
    if hot:
        runmode = 'HOT'
    else:
        runmode = 'DRY'
    logger.info(f'run_command {runmode} {" ".join(command)}')
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
    timestamp = create_timestamp()

    # stop flatcat_ux0 application
    # tmux kill-session -t flatcat
    cmd_line = ['tmux', '-S', '/home/pi/tmux-sock', 'kill-session', '-t', 'flatcat']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

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
        # _, kwargs['install_version'] = get_current_remote()
        _, kwargs['install_version'] = get_current_local(f'{base_work}')

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

    cmd_line = ['rm', f'{base_work}/{filename}']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # run pre-install script
    cmd_line = ['python', f'{base_local}/{dir_flatcatapp}/updater/updater-pre.py']
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

    cmd_line = ['rm', f'{base_work}/{filename}']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # run post-install script
    # install crontab
    cmd_line = ['python', f'{base_local}/{dir_flatcatapp}/updater/updater-post.py']
    # '--backup', base_local_old]
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # # stop gunicorn api server
    # # TODO fix self-kill
    # cmd_line = ['pkill', 'gunicorn']
    # cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    # commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})

    # application restart
    # /home/pi/jetpack/bootscripts/starttmux.sh
    # /home/pi/jetpack/setup/boot/start-tmux.sh
    cmd_line = [f'{base_local}/{dir_flatcatsetup}/boot/start-tmux.sh']
    cmd_status, cmd_output = run_command(cmd_line, kwargs['run_hot'])
    commands.append({'cmd_line': cmd_line, 'cmd_status': cmd_status, 'cmd_output': cmd_output})
    
    return {
        'commands': commands
    }

def configuration_get_wifi(*args, **kwargs):
    """configuration_get_wifi

    Get the Wifi configurations from
    /etc/wpa_supplicant/wpa_supplicant.conf and return JSON dictionary.
    """
    wpa_conf_text = ''
    # get wpa_supplicant path from config
    # open wpa_supplicant
    with open(config_wpa_path, 'r') as f:
        wpa_conf_text = f.read()
    logger.info(f'configuration_get_wifi wpa_conf_text = {wpa_conf_text}')

    with open(config_flatcat_path, 'r') as f:
        config_flatcat = json.load(f)
        logger.info(f'configuration_get_wifi config_flatcat = {json.dumps(config_flatcat, indent=4)}')

def configuration_get_all(*args, **kwargs):
    """configuration_get_all

    Get the entire configuration dict from config_flatcat.json
    """
    config_flatcat = {}
    logger.info(f'configuration_get_all cwd {os.getcwd()}, config_flatcat_path {config_flatcat_path}')
    with open(config_flatcat_path, 'r') as f:
        config_flatcat = json.load(f)
        # print(f'config_flatcat = {json.dumps(config_flatcat, indent=4)}')
    return config_flatcat

def configuration_set(*args, **kwargs):
    """configuration_set

    Set a configuration option and write back to file
    """
    config_flatcat = {}
    logger.info(f'configuration_set')
    with open(config_flatcat_path, 'r') as f:
        config_flatcat = json.load(f)
        logger.info(f'config_flatcat = {json.dumps(config_flatcat, indent=4)}')

    if kwargs['address'] is None:
        config_flatcat_new = kwargs['value']
        config_flatcat.update(config_flatcat_new)
        configuration_write(config_flatcat)
        return
        
    # kwargs[key] = wifi/0/ssid
    # kwargs[value] = mywifi
    address_items = kwargs['address'].split('/')
    _ = config_flatcat
    for k in address_items[:-1]:
        if re.match("^\d*$", k):
            k = int(k)
        _ = _[k]

    k = address_items[-1]
    if re.match("^\d*$", k):
        k = int(k)
    _[k] = kwargs['value']

    logger.info(f'config_flatcat post update {config_flatcat}')
    configuration_write(config_flatcat)

def configuration_write(*args, **kwargs):
    """configuration_set

    Set a configuration option and write back to file
    """
    logger.info(f'configuration_write')
    with open(config_flatcat_path, 'w') as f:
        json.dump(args[0], f, indent=4)

def configuration_wifi_write(*args, **kwargs):
    """configuration_wifi_write

    Write the configuration from `config_flatcat` into system file
    /etc/wpa_supplicant/wpa_supplicant.conf and return JSON dictionary.
    """
    # TODO if live
    if flatcat_live():
        run_hot = True
    else:
        run_hot = False

    # get wpa_supplicant path from config
    # open wpa_supplicant
    # with open(config_wpa_path, 'w') as f:
    with tempfile.NamedTemporaryFile(mode='w') as f:
        conf = """ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=DE
"""

        """network={
    ssid="WLAN1-T93J53"
    psk="D8D9he9TE5e2Fy1e"
    scan_ssid=1
    id_str="AP1"
}
network={
    ssid="0tterwechsel::2GHz4"
    psk="Tagtraeumer, verdraengen die Kaelte dieser Stadt"
    scan_ssid=1
    id_str="AP2"
}
network={
    ssid="flatcat"
    psk="password"
    scan_ssid=1
    id_str="AP3"
}
        """

        conf += "network={\n"
        # conf += str(kwargs['configuration_wifi'])
        for (k, v) in kwargs['configuration_wifi'].items():
            if k not in ['ssid', 'psk', 'scan_ssid', 'id_str']: continue
            if k == 'scan_ssid':
                conf += f'    {k}={v}\n'
            else:
                conf += f'    {k}="{v}"\n'
        conf += "}"
        f.write(conf)
        f.flush()
        logger.info(f'configuration_wifi_write wpa_conf_text {conf}')
        logger.info(f'configuration_wifi_write wpa_conf_file {f.name}')
        cmd_line = ['sudo', 'cp', f.name, config_wpa_path]
        run_command(cmd_line, hot=run_hot)

    # TODO reload wifi config on system
    # https://raspberrypi.stackexchange.com/questions/73749/how-to-connect-to-wifi-without-reboot
    """
    sudo systemctl daemon-reload
    sudo systemctl restart dhcpcd

    # or

    sudo systemctl restart wpa_supplicant@wlan0.service
    sudo systemctl daemon-reload
    """
    # cmd_line = ['sudo', 'systemctl', 'restart', 'wpa_supplicant@wlan0.service']
    # run_command(cmd_line, hot=run_hot)
    # # cmd_line = ['sudo', 'systemctl', 'restart', 'dhcpcd']
    # cmd_line = ['sudo', 'systemctl', 'daemon-reload']
    # run_command(cmd_line, hot=run_hot)
    cmd_line = ['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure']
    run_command(cmd_line, hot=run_hot)

def flatcat_live(*args, **kwargs):
    """flatcat_live

    Test if we are on a live system or on a development staging system
    """
    os_release_path = '/etc/os-release'
    if not os.path.exists(os_release_path):
        return False
    with open(os_release_path, 'r') as f:
        os_release_dict = dict([[__.replace('"', '') for __ in _.strip().split('=')] for _ in f.readlines()])

    logger.info(f'flatcat_live: os_release_dict = {os_release_dict}')
    if os_release_dict['ID'] == 'raspbian':
        return True
    else:
        return False

def configuration_wifi_connected_iwgetid(*args, **kwargs):
    cmd_line = ['/sbin/iwgetid', 'wlan0']
    res = run_command(cmd_line, hot=True)
    if not res[0]:
        cmd_line = ['/sbin/iwgetid']
        res = run_command(cmd_line, hot=True)
    res = res[1].strip()
    res_iface = res.split(' ')[0]
    res_essid = res.split(':')[-1].replace("\"", "")
    return {
        'iface': res_iface,
        'essid': res_essid,
    }

# system
def system_shutdown():
    if flatcat_live():
        run_hot = True
    else:
        run_hot = False

    cmd_line = ['sudo', 'halt']
    res = run_command(cmd_line, hot=run_hot)
    return res

def system_restart():
    cmd_line = ['ls']
    res = run_command(cmd_line, hot=True)
    return res
