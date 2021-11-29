import sys
from typing import Dict, Optional, Union
import time
from flask import (
    current_app,
    Flask,
    json,
    request,
    Response,
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
)

app = Flask(__name__)

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

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/updater/version')
def api_updater_version() -> Response:
    return api_response_ok(
        {'message': 'version',
         'version': get_version_tag(base_local)
        }
    )

# update list: list available local updates
@app.route('/api/updater/list') # methods=['POST']
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
@app.route('/api/updater/current') # methods=['POST']
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
@app.route('/api/updater/download', methods=['POST'])
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
@app.route('/api/updater/install', methods=['POST'])
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
