import pymunk

from kivy.graphics import *

import physics


class Bullet:
    radius = .2
    timer = 0

    def __init__(self, app):
        self.app = app

        self.body = pymunk.Body()
        self.collider = pymunk.Circle(self.body, self.radius)
        self.collider.parent = self
        self.collider.mass = 2
        self.collider.collision_type = physics.BULLET

        self.collider.filter = pymunk.ShapeFilter(categories=physics.BULLET_FILTER,
                                                  mask=pymunk.ShapeFilter.ALL_MASKS ^ physics.BULLET_FILTER)

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            self.color = Color(1, 0, 0)
            self.pos = Translate()
            app.graphic_data.draw_mesh('models/bullet', self.canvas, texture=None)

            PopMatrix()

        self.dy = 0

    def spawn(self, pos, vel, speed, color):
        self.color.rgb = color
        self.body.position = pos[::2]
        self.body.velocity = [i * speed for i in vel[::2]]
        self.pos.xyz = pos
        self.dy = vel[1] * speed

        self.timer = 1

        self.app.physics.space.add(self.body, self.collider)
        self.app.renderer.scene.add(self.canvas)

    def update(self, dt):
        self.pos.x = self.body.position.x
        self.pos.z = self.body.position.y
        self.pos.y += self.dy * dt

        i = self.timer // .02
        self.timer -= dt * .3
        if self.timer < 0:
            self.app.game_manager.remove_object(self)
        elif i != self.timer // .02:
            test_particle = self.app.resource_manager.get_particle(self.pos.xyz, (0, 0, 0), 1)
            self.app.renderer.scene.add(test_particle.canvas)
            self.app.game_manager.game_objects.add(test_particle)

    def despawn(self):
        if self.body in self.app.physics.space.bodies:
            self.app.renderer.scene.remove(self.canvas)
            self.app.physics.space.remove(self.body, self.collider)
            self.app.resource_manager.cache_bullet(self)
