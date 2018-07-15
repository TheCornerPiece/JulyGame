import pymunk

from kivy.graphics import *

import physics


class Staircase:
    size = 2, 2
    height = 4

    def __init__(self, app, pos, angle):
        self.app = app

        t = pymunk.Transform(a=self.size[0], b=0,
                             c=0, d=self.size[1],
                             tx=pos[0], ty=pos[2])

        self.collider = pymunk.Poly(self.app.physics.space.static_body,
                                    vertices=[(i, j) for i in (-1, 1) for j in (-1, 1)],
                                    transform=t)

        self.collider.y = pos[1]
        self.collider.height = self.height
        self.collider.collision_type = physics.STATIC

        self.app.physics.space.add(self.collider)

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            self.pos = Translate(*pos)
            self.rot = Rotate(angle, 0, 1, 0)

            self.app.graphic_data.draw_mesh('models/staircase',
                                            self.canvas,
                                            texture=None)

            PopMatrix()

    def update(self, dt):
        pass

    def despawn(self):
        self.app.physics.space.remove(self.collider)
        self.app.renderer.scene.remove(self.canvas)
