import sys, time
from typing import Dict, Optional, Union
from flask import (
    current_app,
    Flask,
    json,
    request,
    Response,
    Blueprint,
)
# sys.path.insert(0, '/home/src/QK/jetpack/flatcat-app')
# print(sys.path)

from config import (
    base_local,
    base_url,
    base_work,
)

from flatcat.common import (
    download_from_url_into_file,
    get_current_remote,
    get_download_url,
    get_list_remote,
    get_version_tag,
    updater_download,
    updater_install,
    configuration_get_all,
    configuration_set,
    configuration_wifi_write,
    configuration_wifi_connected_iwgetid,
)

# app = Flask(__name__)
api = Blueprint('api', __name__)

def api_response_ok(data: Union[dict, list], status: int = 200) -> Response:
    rv = {'status': 'ok', 'data': data}
    return Response(
        json.dumps(rv),
        content_type='application/json',
        status=status
    )


def api_response_accepted(data: Union[dict, list], location: str) -> Response:
    """
    Send a 202 Accepted Response with a link to the status resource
    in the Location header
    """
    rv = {'status': 'accepted', 'data': data}
    response = Response(
        json.dumps(rv),
        content_type='application/json',
        status=202
    )
    response.headers['Location'] = location
    return response


def api_response_error(
    data: Dict[str, Union[str, dict, list]] = None,
    status: int = 400
) -> Response:
    rv = {'status': 'error', 'data': data}
    return Response(
        json.dumps(rv),
        content_type='application/json',
        status=status
    )

# def get_file_to_disk():
#     r = http.request(
#         'GET',
#         call_url,
#         headers=headers,
#     )
#     if r.status == 200:
#         open(os.path.basename(location), 'wb').write(r.data)
#         print("downloaded {0}".format(location))

#     res = {'status': r.status}
#     if with_result:
#         res.update(json.loads(r.data.decode('utf-8')))
#     return res

# def get_file_contents(call_url):
#     r = http.request(
#         'GET',
#         call_url,
#         headers=headers,
#     )
#     if r.status == 200:
#         open(os.path.basename(location), 'wb').write(r.data)
#         print("downloaded {0}".format(location))

#     res = {'status': r.status}
#     if with_result:
#         res.update(json.loads(r.data.decode('utf-8')))
#     return res

@api.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@api.route('/api/updater/version')
def api_updater_version() -> Response:
    return api_response_ok(
        {'message': 'version',
         'version': get_version_tag(base_local)
        }
    )

# update list: list available local updates
@api.route('/api/updater/list') # methods=['POST']
def api_updater_list() -> Response:
    call_url = 'https://base.jetpack.cl/flatcat/updates/'
    list_of_updates = get_list_remote(call_url)
    return api_response_ok(
        {'message': 'list',
         'url': f'{call_url}',
         'list_of_updates': list_of_updates,
        }
    )

# update check: check remote url if current.bin is greater than / in local files
@api.route('/api/updater/current') # methods=['POST']
def api_updater_current() -> Response:
    # url = request.json.get('url')
    # task_url = "https://jetpack.cl"
    call_url = 'https://base.jetpack.cl/flatcat/updates/current.txt'
    current_file, current_version = get_current_remote(call_url)
    return api_response_ok(
        {'message': 'current',
         'url': f'{call_url}/current.txt',
         'current_file': current_file,
         'current_version': current_version
        }
    )

# update download: download current.bin from remote url
@api.route('/api/updater/download', methods=['POST'])
def api_updater_download() -> Response:
    # url = request.json.get('url')
    # task_url = "https://jetpack.cl"
    # call_url = 'https://base.jetpack.cl/flatcat/updates/download.txt'
    current_app.logger.info(f'request = {request.json}')
    install_version = request.json.get('install_version')

    res = updater_download(**request.json)

    res['message'] = 'download'
    
    return api_response_ok(res)

# update apply / install: apply selected update
@api.route('/api/updater/install', methods=['POST'])
def api_updater_install() -> Response:
    current_app.logger.info(f'request = {type(request.json)}')
    current_app.logger.info(f'request = {request.json.keys()}')
    install_version = request.json.get('install_version')
    install_backup = request.json.get('install_backup')
    run_hot = request.json.get('run_hot')
    
    res = updater_install(**request.json)
    res['message'] = 'install'
    
    return api_response_ok(res)

# settings: send OSC: toggle, use GET / POST
# update apply / install: apply selected update
@api.route('/api/configuration', methods=['GET'])
def api_configuration() -> Response:
    res = configuration_get_all()
    return api_response_ok(res)

@api.route('/api/configuration/wifi/ssid', methods=['GET'])
def api_configuration_wifi_ssid() -> Response:
    res = {'wifi': configuration_get_all()['wifi']['networks'][0]['ssid']}
    return api_response_ok(res)

@api.route('/api/configuration/wifi/psk', methods=['GET'])
def api_configuration_wifi_psk() -> Response:
    res = {'psk': configuration_get_all()['wifi']['networks'][0]['psk']}
    return api_response_ok(res)

@api.route('/api/configuration/wifi', methods=['GET', 'POST'])
def api_configuration_wifi() -> Response:
    if request.method == 'POST':
        current_app.logger.info(f'request = {request.json}')
        configuration_set(address='wifi/networks/0', value=request.json)
        configuration_wifi_write(configuration_wifi=request.json)
        return api_response_ok({
            'message': 'wifi/networks/0 updated'
        })
    elif request.method == 'GET':
        res = {'wifi': configuration_get_all()['wifi']['networks'][0]}
        current_app.logger.info(f'configuration_wifi response = {res}')
        return api_response_ok(res)

@api.route('/api/configuration/wifi/connected', methods=['GET'])
def api_configuration_wifi_connected() -> Response:
    res_iwgetid = configuration_wifi_connected_iwgetid()
    res = {'connected': res_iwgetid}
    return api_response_ok(res)
