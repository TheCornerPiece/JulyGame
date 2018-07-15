import random

from kivy.graphics import *


class Particle:
    def __init__(self, app):
        self.app = app

        self.vel = [0, 0, 0]
        self.angular_velocity = 0

        self.fade_timer = 1

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            self.pos = Translate()

            self.canvas.add(self.app.renderer.particle_yaw)
            self.canvas.add(self.app.renderer.particle_pitch)

            self.roll = Rotate(0, 0, 0, 1)
            self.color = Color(1, 1, 1, 1)

            self.app.graphic_data.draw_mesh('models/rectangle',
                                            self.canvas,
                                            'nana.png')

            PopMatrix()

    def spawn(self, pos, vel):
        self.pos.xyz = pos
        self.vel = vel
        self.color.a = 1
        self.fade_timer = 1

        self.angular_velocity = (random.random() * .5 + .5) * random.choice((-360, 360))

    def despawn(self):
        self.app.resource_manager.cache_particle(self, 0)
        self.app.renderer.scene.remove(self.canvas)

    def update(self, dt):
        self.roll.angle += dt * self.angular_velocity

        self.fade_timer -= dt * .5
        if self.fade_timer > 0:
            self.color.a = self.fade_timer
            self.pos.x += self.vel[0] * dt
            self.pos.y += self.vel[1] * dt
            self.pos.z += self.vel[2] * dt
        else:
            self.app.resource_manager.cache_particle(self)
            self.app.renderer.scene.remove(self.canvas)
            self.app.game_manager.game_objects.remove(self)
