import pymunk

import physics, util


class DynamicObject:
    gravity = 25

    step_height = 1.5

    def __init__(self, app, player=None):
        self.app = app
        self.player = player

        self.body = pymunk.Body()
        self.body.velocity_func = self.velocity_func

        self.dy = 0
        self.standing = False
        self.colliding = set()

    def get_pos(self):
        return self.body.position.x, self.collider.y, self.body.position.y

    def set_pos(self, pos):
        self.body.position = pos[::2]
        self.body.velocity *= 0
        self.collider.y = pos[1]
        self.dy = 0

    def spawn(self, pos):
        self.set_pos(pos)
        self.app.physics.space.add(self.body, self.collider)

    def despawn(self):
        self.app.physics.space.remove(self.body, self.collider)

    def spawn_collider(self, app, shape, y=0, height=1):
        self.collider = shape
        self.collider.body = self.body
        self.collider.parent = self
        self.collider.y = y
        self.collider.height = height
        self.collider.mass = 1
        self.collider.collision_type = physics.DYNAMIC

    def velocity_func(self, body, gravity, damping, dt):
        return pymunk.Body.update_velocity(body, gravity, 0.95, dt)

    def removed_standing(self):
        if self.collider.y > self.step_height:
            for c in self.colliding:
                low_step = self.collider.y - self.step_height
                high_step = self.collider.y + self.step_height
                if low_step < c.y + c.height < high_step:
                    self.dy = 0
                    break
            else:
                self.dy = 10
        else:
            self.dy = 0

        if self.player:
            self.player.removed_standing()

    def set_standing(self, c, shape=True):
        if self.player:
            if self.player.set_standing(c, shape):
                return True

        if shape:
            self.collider.y = c.y + c.height
            self.standing = c
        else:
            self.collider.y = c
            self.standing = True

    def add_collider(self, c):
        if c not in self.colliding:
            self.colliding.add(c)
            top = c.y + c.height
            if top - self.step_height < self.collider.y < top:
                self.set_standing(c)

    def remove_collider(self, other):
        if other in self.colliding:
            self.colliding.remove(other)
            if other is self.standing:
                self.standing = None
                self.removed_standing()

    def get_velocity(self):
        return self.body.velocity.get_length()

    def move_y(self, dt):
        last_y = float(self.collider.y)
        self.collider.y += self.dy * dt
        if self.dy < 0:
            if self.collider.y < 0:
                self.set_standing(0, False)
                self.collider.y = 0
                self.dy *= -1
                self.standing = True
            else:
                for other in self.colliding:
                    top = other.y + other.height
                    if top - self.step_height < self.collider.y <= top:
                        if not self.set_standing(other):
                            return True

        else:
            for other in self.colliding:
                if last_y <= other.y - self.collider.height < self.collider.y:
                    self.collider.y = other.y - self.collider.height
                    self.dy = 0

    def update(self, dt):
        if self.standing and self.standing is not True:
            self.collider.y = self.standing.y + self.standing.height
