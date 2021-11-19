import sys

from updaterlib import (
    create_directories,
    updater_parser
)
from updaterlogger import create_logger

logger = create_logger(sys.argv[0], 'info')

def main_download(args):
    logger.info(f"main_download API")

def main_install(args):
    ret = f"main_install API"
    logger.info(ret)
    return ret

def main_uuid(args):
    logger.info(f"main_uuid API")

def main_package(args):
    logger.info(f"main_package API")

def main_upload(args):
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
