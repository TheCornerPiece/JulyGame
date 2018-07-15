
from kivy.graphics import *


class HealthBar:
    def __init__(self, app):
        self.app = app

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()
            self.color = Color(1, 0, 0, 1)

            self.pos = Translate()
            self.yaw = Rotate(0, 0, 1, 0)
            self.pitch = Rotate(0, 1, 0, 0)
            Translate(-1, 0, 0)
            self.scale = Scale()

            self.app.graphic_data.draw_mesh('models/health_bar',
                                            self.canvas,
                                            texture=None)

            PopMatrix()

    def despawn(self):
        self.app.renderer.scene.remove(self.canvas)

    def update(self, dt):
        self.yaw.angle = -self.app.renderer.cam_yaw.angle
        self.pitch.angle = -self.app.renderer.cam_pitch.angle
