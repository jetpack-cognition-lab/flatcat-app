import sys
import requests
import json

from flatcat.common import (
    create_directories,
    updater_parser
)
from flatcat.logging import create_logger

logger = create_logger(sys.argv[0], 'info')

api_url = "http://localhost:5000"

def main_list(args):
    """main_list

    get list of updates from server / API
    """
    logger.info(f"main_list API")
    call_url = f"{api_url}/updater/list"
    r = requests.get(
        call_url
    )
    logger.info(f'response raw {r.text}')
    res = json.loads(r.text)
    return res

def main_current(args):
    """main_current

    get most current update from server / API
    """
    logger.info(f"main_current API")
    call_url = f"{api_url}/updater/current"
    r = requests.get(
        call_url
    )
    logger.info(f'response raw {r.text}')
    res = json.loads(r.text)
    return res
    
def main_download(args):
    """main_download

    Download update from server / API
    """
    logger.info(f"main_download API")
    # call API download function

def main_install(args):
    """main_download

    Install update from local storage (after download)
    """
    ret = f"main_install API"
    logger.info(ret)
    return ret

def main_uuid(args):
    """main_uuid

    Create a short UUID
    """
    logger.info(f"main_uuid API")

def main_package(args):
    """main_package

    Package an update from the current local build
    """
    logger.info(f"main_package API")

def main_upload(args):
    """main_upload

    Upload a packaged update from the current local build
    """
    logger.info(f"main_upload API")

if __name__ == '__main__':
    parser = updater_parser()
    args = parser.parse_args()
    args.installed_version = '20211001'
    # 20211202
    logger.info(f'{sys.argv[0]}__main__ args = {args}')

    # check directories / initialize
    create_directories()
    
    if args.mode == 'download':
        _main = main_download
    elif args.mode == 'install':
        _main = main_install
    elif args.mode == 'current':
        _main = main_current
    elif args.mode == 'list':
        _main = main_list
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
