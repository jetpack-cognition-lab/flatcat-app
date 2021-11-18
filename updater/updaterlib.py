"""flatcat-app/updater

updaterlib
"""
import os
import string
import random
import requests

from datetime import datetime
from clint.textui import progress
from subprocess import run, CalledProcessError

from config import (
    base_url,
    base_hostname,
    base_home,
    base_local,
    base_work
)

VERBOSE = True

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
