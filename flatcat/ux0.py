"""DataThread

Data generator using real time data from the flatcat_ux0 robot
controller.

To be used in the context of a flask app
"""

import socket, threading, random, time

class DataThread(threading.Thread):
    def __init__(self, app = None, socketio = None, thread_stop_event = None):
        self.app = app
        self.socketio = socketio
        self.thread_stop_event = thread_stop_event
        super(DataThread, self).__init__()
        self.delay = 1.0
        self.daemon = True
        self.is_connected = False
        self.app.logger.info(f'{self.__class__.__name__} init socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = 'flatcat3000.local'
        self.port = 7332
        self.bufsize  = 4096
        self.soc = -1
        self.app.logger.info(f'{self.__class__.__name__} socket connect {self.address}:{self.port}')
        self.sock.connect((self.address, self.port))
        
        self.app.logger.info(f'{self.__class__.__name__} socket local  {self.sock.getsockname()}')
        self.app.logger.info(f'{self.__class__.__name__} socket remote {self.sock.getpeername()}')
        self.is_connected = True

    def parse_message(self, msg):
        li = msg.split("=", 1)
        if len(li)>1:
            return li[1]
        print("message faulted: {0}".format(msg))
        return ""

    def receive(self):
        try:
            msg=self.sock.recv(self.bufsize)
            msg = msg.decode('utf8').strip()
            # self.app.logger.info(f"{self.__class__.__name__} received <{msg}>")
            return msg
        except KeyboardInterrupt:
            self.app.logger.error("{self.__class__.__name__} aborted")
        return ""

    def send(self, msg):
        numbytes = self.sock.send(msg.encode('utf8'))
        # self.app.logger.info(f"{self.__class__.__name__} message sent bytes {numbytes}")
                
    def receive_ack(self):
        if (self.receive() != "ACK\n"): 
            print("No response")

    def send_command(self, cmd):
        self.send(cmd)
        self.receive_ack()

    def request_variable(self, keystr):
        cmd = keystr+"\n"
        self.send(cmd)
        return self.receive_variable()

    def receive_variable(self):
        msg = self.receive()
        return self.parse_message(msg)

    def dataGenerator(self):
        self.app.logger.info("{self.__class__.__name__} dataGenerator init")
        try:
            while not self.thread_stop_event.isSet():

                if self.is_connected:
                    # cmd = "HELLO"
                    # self.send(cmd)
                    self.soc = float( self.request_variable("SoC") )
                    # self.app.logger.info(f'{self.__class__.__name__} dataGenerator SoC {self.soc}')
                    temperature = self.soc
                    # socketio.emit('responseMessage', {'temperature': self.soc})
                else:
                    temperature = round(random.random()*10, 3)

                self.app.logger.info(f'{self.__class__.__name__} dataGenerator temperature {temperature}')
                self.socketio.emit('responseMessage', {'temperature': temperature})

                time.sleep(self.delay)

        except KeyboardInterrupt:
            # kill()
            self.app.logger.info("Keyboard Interrupt")

            cmd = "EXIT\n"
            self.send(cmd)
            self.app.logger.info("Keyboard Interrupt closing socket")
            self.sock.close()
            
    def run(self):
        self.dataGenerator()

