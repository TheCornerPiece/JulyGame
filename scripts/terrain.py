from kivy.graphics import *


class Terrain:
    def __init__(self, app, filename, texture):
        self.app = app

        self.canvas = Canvas()

        with self.canvas.before:
            PushMatrix()
            Color((1, 1, 1))
            self.app.graphic_data.draw_mesh(filename, self.canvas, texture)
            PopMatrix()

