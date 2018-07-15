import pymunk


class ServerPhysics:
    clients = {}
    objects = {}

    def __init__(self):
        self.space = pymunk.Space()

    def spawn_object(self):
        object_id = -1

        body = pymunk.Body()
        collider = pymunk.Circle(body, 5)
        collider.mass = 1
        self.space.add(body, collider)
        self.objects[object_id] = body

    def add_client(self, client_id):
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        collider = pymunk.Circle(body, 1)

        self.space.add(body, collider)

        self.clients[client_id] = body

    def move_client(self, client_id, pos):
        self.clients[client_id].position = pos[::2]
