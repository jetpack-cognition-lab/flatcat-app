import threading
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
from flask import (
    Flask)

from config import (
    socketio_enabled
)

from api import api as api_blueprint

from flatcat.ux0 import DataThread

app = Flask(
    __name__,
    template_folder='templates'
)

app.config['SECRET_KEY'] = 'mysecret'

# need this
app.logger.info(f'app.py type(api_blueprint) {type(api_blueprint)}')
app.register_blueprint(api_blueprint)

# socketIo = SocketIO(app)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')
CORS(app)

app.debug = True
app.host = 'localhost'

thread = threading.Thread()
thread_stop_event = threading.Event()

# @socketIo.on("message")
# def handleMessage(msg):
#     # print(msg)
#     app.logger.info(f'message {msg}')
#     send(msg, broadcast=True)
#     return None

def root():
    return render_template('main.html')

# TODO create async communication thread with flatcat_ux0 and 'send' out the data

# Handle the webapp connecting to the websocket
@socketio.on('connect')
def test_connect():
    app.logger.info('someone connected to websocket')
    emit('responseMessage', {'data': 'Connected! ayy'})
    # need visibility of the global thread object
    global thread
    if not thread.is_alive():
        app.logger.info("Starting Thread")
        thread = DataThread(app, socketio, thread_stop_event)
        # thread.daemon = True
        thread.start()
        app.logger.info("Starting Thread Done")

# Handle the webapp connecting to the websocket, including namespace for testing
@socketio.on('connect', namespace='/devices')
def test_connect2():
    app.logger.info('someone connected to websocket!')
    emit('responseMessage', {'data': 'Connected devices! ayy'})

# Handle the webapp sending a message to the websocket
@socketio.on('message')
def handle_message(message):
    # app.logger.info('someone sent to the websocket', message)
    app.logger.info('Data', message["data"])
    app.logger.info('Status', message["status"])
    global thread
    global thread_stop_event
    if (message["status"]=="Off"):
        if thread.isAlive():
            thread_stop_event.set()
        else:
            app.logger.info("Thread not alive")
    elif (message["status"]=="On"):
        if not thread.isAlive():
            thread_stop_event.clear()
            app.logger.info("Starting Thread")
            # thread = DataThread()
            thread.start()
    else:
        app.logger.info("Unknown command")


# Handle the webapp sending a message to the websocket, including namespace for testing
@socketio.on('message', namespace='/devices')
def handle_message2():
    app.logger.info('someone sent to the websocket!')


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    app.logger.info('An error occured:')
    app.logger.info(e)


if __name__ == '__main__':

    # app.register_blueprint(api)
    # app.run()
    # socketIo.run(app)
    socketio.run(app, debug=True, host='0.0.0.0')
