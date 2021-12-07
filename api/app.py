from flask_socketio import SocketIO, send
from flask import (
    Flask)

from api import api

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'

socketIo = SocketIO(app, cors_allowed_origins="*")
# CORS(app)
# socketIo = SocketIO(app)

app.debug = True
app.host = 'localhost'

@socketIo.on("message")
def handleMessage(msg):
    # print(msg)
    app.logger.info(f'message {msg}')
    send(msg, broadcast=True)
    return None

# TODO create async communication thread with flatcat_ux0 and 'send' out the data

if __name__ == '__main__':

    app.register_blueprint(api)
    
    # app.run()
    socketIo.run(app)
