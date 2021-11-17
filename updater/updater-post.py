"""flatcat-app/updater

post-install tasks
"""
from pprint import pformat

def flatcat_config_read_to_dict(conffile):
    with open(conffile, 'r') as f:
        conftext = [_.strip() for _ in f.readlines() if _ not in ['\n']]
        # print(f"conftext = {conftext}")
        confdict = [[a.strip().replace('{', '').replace('}', '') for a in _.split('=')] for _ in conftext]
        confdict = dict([(_[0], float(_[1])) for _ in confdict])
        # print(f"confdict = {confdict}")
        return confdict

def flatcat_config_dict_to_file(conffile, conf):
    with open(conffile, 'w') as f:
        for k, v in conf.items():
            f.write(f'{k} = {{{v}}}\n')

if __name__ == '__main__':
    print(f'updater-post')
    # post-install tasks
    package_post_install_tasks = [
        'update flatcat.dat',
        'update system config',
        'update crontab',
        'check / create venv',
    ]
    print(f'package_post_install_tasks =\n{pformat(package_post_install_tasks)}')

    # read local config
    conf1 = flatcat_config_read_to_dict('flatcat-ux0/flatcat.dat')
    print(f"conf1 = \n{pformat(conf1)}")

    # read new default config
    conf2 = flatcat_config_read_to_dict('flatcat-ux0/flatcat.dat.dist')
    print(f"conf2 = \n{pformat(conf2)}")

    # create new config
    conf3 = {}
    # update with new defaults
    conf3.update(conf2)
    #  conserve custom settings
    conf3.update(conf1)
    print(f"conf3 = \n{pformat(conf3)}")

    # write new config to file
    flatcat_config_dict_to_file('flatcat-ux0/flatcat.dat', conf3)
