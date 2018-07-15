import pymunk

from scripts import character

import dynamic_object, util


class NetPlayer:
    state = 0
    attacking = False
    vehicle = None
    input_vector = [0, 0]

    radius = 1
    height = 4.5

    target_angle = 0
    target_pos = [0, 0, 0]
    velocity = 0

    def __init__(self, app, client_id):
        self.app = app
        self.client_id = client_id

        self.collision = dynamic_object.DynamicObject(self.app, self)
        self.collision.body.body_type = pymunk.Body.KINEMATIC

        self.collision.spawn_collider(self.app, pymunk.Circle(None, self.radius),
                                      0, self.height)

        self.collision.spawn((0, 0, 0))

        self.graphics = character.Character(self.app)

    def despawn(self):
        self.app.renderer.scene.remove(self.graphics.canvas)
        self.collision.despawn()

    def set_standing(self, c, shape=True):
        pass

    def removed_standing(self):
        pass

    def get_velocity(self):
        return self.velocity

    def set_pos(self, pos):
        self.target_pos = pos[:3]
        self.velocity = pos[3]

    def set_angle(self, angle):
        self.target_angle = angle

    def set_state(self, state):
        self.state = state

    def update(self, dt):
        self.graphics.rot.angle += (self.target_angle - self.graphics.rot.angle) * .3
        new_pos = [i + (j - i) * .3 for i, j in zip(self.graphics.pos.xyz, self.target_pos)]
        self.graphics.pos.xyz = new_pos
        self.collision.body.position = new_pos[::2]
        self.collision.collider.y = new_pos[1]

        self.graphics.do_animation(self, dt)
