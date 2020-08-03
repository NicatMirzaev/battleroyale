import socket
import _pickle as pickle
class Client:
    """
    class to connect, send and recieve information from the server

    need to hardcode the host attirbute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.100.2"
        self.port = 5555
        self.addr = (self.host, self.port)

    def connect(self, name):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int reprsenting id
        """
        self.client.connect(self.addr)
        self.client.send(str.encode(name))
        val = self.client.recv(50)
        return val.decode()

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """

        self.client.close()

    def send(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            if pick:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))

            reply = self.client.recv(2048)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print("[EXCEPTION] ", e)

            return reply
        except socket.error as e:
            print("[EXCEPTION] ", e)