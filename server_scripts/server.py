from twisted.internet import reactor
from twisted.internet import protocol


class ClientInfo:
    client_id = 0
    pos = [0, 0, 0]
    angle = 0
    state = 0


class Server(protocol.DatagramProtocol):
    conns = set()
    current_id = -1

    def __init__(self, app):
        self.app = app

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

    def datagramReceived(self, data, addr):
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

    def start(self, port=7999):
        reactor.listenUDP(port, self)

    def makeConnection(self, transport):
        print transport

    def get_new_id(self):
        self.current_id += 1
        return self.current_id

    def register_conn(self, conn):
        conn.conn_id = self.get_new_id()
        self.conns.add(conn)
        self.dispatch('{}|n;'.format(conn.conn_id), [conn])
        message = ''
        for c in self.conns:
            if c is not conn:
                message += '{}|n;'.format(c.conn_id)
                message += '{}|p|{};'.format(c.conn_id, c.get_pos())
                message += '{}|a|{};'.format(c.conn_id, c.get_angle())
                message += '{}|s|{};'.format(c.conn_id, c.get_state())
        #
        # for object_id, object in self.app.physics.objects:
        #     message += '{}'.format(object.position.x)

        self.dispatch(message, [conn], False)

    def remove_conn(self, conn):
        print 'connection lost'
        self.conns.remove(conn)
        self.dispatch('{}|r;'.format(conn.conn_id))

    def dispatch(self, message, conns=[], exclude_list=True):
        data = message.encode('utf-8')
        if exclude_list:
            for c in self.conns:
                if c not in conns:
                    # print 'send message: {}'.format(message)
                    c.transport.write(data)
        else:
            for c in conns:
                c.transport.write(data)
