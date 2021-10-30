from typing import Dict, Optional, Union
import time
from flask import (
    Flask,
    json,
    Response,
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

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/update/check') # methods=['POST']
def update_check() -> Response:
    # url = request.json.get('url')
    task_url = "https://jetpack.cl"    
    return api_response_ok(
        {'message': 'update_check', 'url': 'https://jetpack.cl/flatcat/current.bin'}
    )

# update list: list available local updates
# update check: check remote url if current.bin is greater than / in local files
# update download: download current.bin from remote url
# update apply: apply selected update

# settings: send OSC: toggle, use GET / POST
