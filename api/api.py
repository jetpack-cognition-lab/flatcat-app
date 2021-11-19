import sys
from typing import Dict, Optional, Union
import time
from flask import (
    Flask,
    json,
    Response,
)

# sys.path.insert(0, '/home/src/QK/jetpack/flatcat-app')
print(sys.path)
from flatcat.common import (
    get_current_remote,
    get_list_remote
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

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

# update list: list available local updates
@app.route('/updater/list') # methods=['POST']
def updater_list() -> Response:
    call_url = 'https://base.jetpack.cl/flatcat/updates/'
    list_of_updates = get_list_remote(call_url)
    return api_response_ok(
        {'message': 'list',
         'url': f'{call_url}',
         'list_of_updates': list_of_updates,
        }
    )

# update check: check remote url if current.bin is greater than / in local files
@app.route('/updater/current') # methods=['POST']
def updater_current() -> Response:
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
@app.route('/updater/download') # methods=['POST']
def updater_download() -> Response:
    # url = request.json.get('url')
    # task_url = "https://jetpack.cl"
    call_url = 'https://base.jetpack.cl/flatcat/updates/download.txt'
    download_file, download_version = download_from_url_into_file()
    return api_response_ok(
        {'message': 'current',
         'url': f'{call_url}/current.txt',
         'current_file': current_file,
         'current_version': current_version
        }
    )

# update apply / install: apply selected update

# settings: send OSC: toggle, use GET / POST
