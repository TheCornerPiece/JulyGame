import random

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import main


class MulticastPingClient(DatagramProtocol):
    ip = "228.0.0.5"
    port = 8005

    def __init__(self, manager):
        self.manager = manager
        self.client_id = random.randint(0, 10000)

    def startProtocol(self):
        self.transport.joinGroup(self.ip)

    def send(self, message):
        self.transport.write('{}|{}'.format(self.client_id, message), (self.ip, self.port))

    def datagramReceived(self, datagram, address):
        self.manager.recv_message(datagram, address)


class NetworkManager:
    def __init__(self, app):
        self.app = app
        self.conn = None

        self.client_ids = set()

    def connect_to_server(self):
        self.conn = MulticastPingClient(self)
        reactor.listenMulticast(MulticastPingClient.port,
                                self.conn, listenMultiple=True)

    def disconnect(self):
        self.send_message('r;')
        reactor.disconnectAll()
        self.conn = None

    def on_connection(self, conn):
        self.conn = conn
        self.send_message('s|{};'.format(self.app.game_manager.player.state))

    def send_message(self, message):
        if self.conn:
            # print 'sending: {}'.format(message)
            self.conn.send(message.encode('utf-8'))

    def recv_message(self, msg, addr):
        messages = msg.split(';')[:-1]
        for message in messages:
            args = message.split('|')
            client_id = int(args[0])

            if client_id != self.conn.client_id:
                if client_id not in self.app.game_manager.net_players:
                    self.app.game_manager.spawn_net_player(client_id)
                    self.client_ids.add(client_id)

                command = args[1]
                data = args[2:]

                game_manager = self.app.game_manager

                if command == 'r':
                    self.client_ids.remove(client_id)
                    game_manager.remove_net_player(client_id)

                elif command == 'p':
                    pos = [float(i) for i in data]
                    game_manager.set_net_player_pos(client_id, pos)

                elif command == 'a':
                    game_manager.set_net_player_angle(client_id, int(args[2]))

                elif command == 's':
                    game_manager.set_net_player_state(client_id, int(args[2]))

                elif command == 'v':
                    self.app.level_manager.levels = self.app.level_manager.get_all_levels()
                    self.app.set_state(main.GAME)
