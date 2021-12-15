"""flatcat-app/updater

post-install tasks
"""
import argparse
import json
from pprint import pformat

from config import (
    base_home,
    base_local,
    base_work,
    dir_flatcatapp,
    dir_flatcatux0,
    dir_flatcatsetup,
)

from flatcat.common import (
    run_command
)

def flatcat_config_read_to_dict(conffile):
    print(f"conffile = {conffile}")    
    conftext = ''
    try:
        with open(conffile, 'r') as f:
            conftext = [_.strip() for _ in f.readlines() if (_ not in ['\n'] and not _.startswith('#'))]
    except FileNotFoundError as e:
        return {}
    
    print(f"conftext = {conftext}")

    # convert to dict by '=' operator
    confdict = [[a.strip() for a in _.split('=')] for _ in conftext]
    confdict = dict(confdict)

    for k, v in confdict.items():
        print(k, v)
        try:
            confdict[k] = int(v)
            continue
        except ValueError as e:
            print(e)

        if v.startswith('{') and ',' not in v:
            # scalar, remove vector braces
            v = v.replace('{', '').replace('}', '')
            confdict[k] = float(v)
            continue

        # otherwise string
        
    
    # types: int, float, string, vector
    
    # convert one vectors to scalar
    # confdict = [[a.strip().replace('{', '').replace('}', '') for a in _.split('=')] for _ in conftext]
    # convert all numbers to float
    # confdict = dict([(_[0], float(_[1])) for _ in confdict])
    print(f"confdict = {confdict}")
    return confdict

def flatcat_config_dict_to_file(conffile, conf):
    with open(conffile, 'w') as f:
        for k, v in conf.items():
            if type(v) in [int, str]:
                f.write(f'{k} = {v}\n')
            elif type(v) is float:
                f.write(f'{k} = {{{v}}}\n')

def flatcat_config2_read_to_dict(conffile):
    try:
        with open(conffile, 'r') as f:
            conftext = [_.strip() for _ in f.readlines() if _ not in ['\n']]
            # print(f"conftext = {conftext}")
            confdict = [[a.strip() for a in _.split('=')] for _ in conftext]
            # confdict = dict([(_[0], float(_[1])) for _ in confdict])
            # print(f"confdict = {confdict}")
            return confdict
    except FileNotFoundError as e:
        return {}

def flatcat_config2_dict_to_file(conffile, conf):
    with open(conffile, 'w') as f:
        for k, v in conf.items():
            f.write(f'{k} = {v}\n')

def flatcat_config3_read_to_dict(conffile):
    try:
        with open(conffile, 'r') as f:
            confdict = json.load(f)
            return confdict
    except FileNotFoundError as e:
        return {}

def flatcat_config3_dict_to_file(conffile, conf):
    with open(conffile, 'w') as f:
        json.dump(conf, f)


def rewrite_flatcatdat(*args, **kwargs):
    """rewrite_flatcatdat

    Rewrite flatcat.dat.dist file to flatcat.dat on update

    - Read dist file
    - Read local file
    - Merge dictionaries
    - Write new local file
    """
    ######################################################################
    # update flatcat.dat from dist file
    conf1 = flatcat_config_read_to_dict(f'{base_local}/{dir_flatcatux0}/flatcat.dat')
    print(f"conf1 = \n{pformat(conf1)}")

    # read new default config
    conf2 = flatcat_config_read_to_dict(f'{base_local}/{dir_flatcatux0}/flatcat.dat.dist')
    print(f"conf2 = \n{pformat(conf2)}")

    # create new config
    conf3 = {}
    # update with new defaults
    conf3.update(conf2)
    #  conserve custom settings
    conf3.update(conf1)
    print(f"conf3 = \n{pformat(conf3)}")

    # write new config to file
    flatcat_config_dict_to_file(f'{base_local}/{dir_flatcatux0}/flatcat.dat', conf3)

def rewrite_configpy():
    ######################################################################
    # TODO do the same for config.py
    conf1 = flatcat_config2_read_to_dict(f'{base_local}/{dir_flatcatapp}/config.py')
    print(f"conf1 = \n{pformat(conf1)}")

    # read new default config
    conf2 = flatcat_config2_read_to_dict(f'{base_local}/{dir_flatcatapp}/config.py.dist')
    print(f"conf2 = \n{pformat(conf2)}")

    # create new config
    conf3 = {}
    # update with new defaults
    conf3.update(conf2)
    #  conserve custom settings
    conf3.update(conf1)
    print(f"conf3 = \n{pformat(conf3)}")

    # write new config to file
    flatcat_config2_dict_to_file(f'{base_local}/{dir_flatcatapp}/config.py', conf3)

def rewrite_configflatcatjson():
    ######################################################################
    # TODO do the same for config_flatcat.json
    conf1 = flatcat_config3_read_to_dict(f'{base_local}/{dir_flatcatapp}/config_flatcat.json')
    print(f"conf1 = \n{pformat(conf1)}")

    # read new default config
    conf2 = flatcat_config3_read_to_dict(f'{base_local}/{dir_flatcatapp}/config_flatcat.json.dist')
    print(f"conf2 = \n{pformat(conf2)}")

    # create new config
    conf3 = {}
    # update with new defaults
    conf3.update(conf2)
    #  conserve custom settings
    conf3.update(conf1)
    print(f"conf3 = \n{pformat(conf3)}")

    # write new config to file
    flatcat_config3_dict_to_file(f'{base_local}/{dir_flatcatapp}/config_flatcat.json', conf3)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backup', type=str, help='Backup directory [None]', default=None)

    args = parser.parse_args()
    
    # print(f'updater-post')
    
    # # post-install tasks
    # package_post_install_tasks = [
    #     'update flatcat.dat',
    #     'update config.py',
    #     'update system config',
    #     'update crontab',
    #     'check / create venv',
    # ]
    # print(f'package_post_install_tasks =\n{pformat(package_post_install_tasks)}')

    # read local config
    # if args.backup is not None:
    #     conf1 = flatcat_config_read_to_dict(f'{args.backup}/{dir_flatcatux0}/flatcat.dat')
    #     print(f"conf1 = \n{pformat(conf1)}")
    # else:
    #     conf1 = {}

    rewrite_flatcatdat()


    rewrite_configpy()

    
    rewrite_configflatcatjson()

    
    # make boot scripts executable
    command = ['chmod', '+x', f'{base_local}/{dir_flatcatsetup}/boot/start-tmux.sh']
    run_command(command, True)
    
    command = ['chmod', '+x', f'{base_local}/{dir_flatcatsetup}/boot/start-ap-managed-wifi.sh']
    run_command(command, True)
