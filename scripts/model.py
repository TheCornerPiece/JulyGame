from kivy.graphics import *

import physics


class Model:
    def __init__(self, app):
        self.app = app

        self.canvas = Canvas()

        with self.canvas.before:
            PushMatrix()

            self.rot = Rotate(0, 0, 1, 0)
            self.pos = Translate()

        with self.canvas.after:
            PopMatrix()

    def set_mesh(self, filename, texture=None):
        with self.canvas:
            self.app.graphic_data.draw_mesh(filename, self.canvas, texture)

    def add_collider(self):
        self.app.resource_manager.get_circle(offset=self.pos.xyz,
                                             radius=2,
                                             height=6,
                                             collision_type=physics.STATIC)
