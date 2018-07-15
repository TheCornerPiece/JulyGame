
from twisted.internet import protocol


class Conn(protocol.DatagramProtocol):
    def __init__(self):
        self.conn_id = None

        self.pos = [0, 0, 0]
        self.angle = 0
        self.state = 0

    def connectionMade(self):
        self.factory.register_conn(self)

    def connectionLost(self, reason):
        self.factory.remove_conn(self)

    def get_pos(self):
        return '|'.join([str(i) for i in self.pos])

    def get_angle(self):
        return self.angle

    def get_state(self):
        return self.state

    def dataReceived(self, data):
        messages = data.decode('utf-8').split(';')[:-1]
        for message in messages:
            args = message.split('|')

            if args[0] == 'p':
                self.pos = [float(i) for i in args[1:]]

            elif args[0] == 'a':
                self.angle = int(args[1])

            elif args[0] == 's':
                self.state = int(args[1])

            self.factory.dispatch('{}|{};'.format(self.conn_id, message), [self])