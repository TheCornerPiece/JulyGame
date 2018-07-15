from kivy.graphics import *

IDLE, DIE = xrange(2)


class Powerup:
    state = -1
    timer = 1

    def __init__(self, app, pos):
        self.app = app

        self.canvas = Canvas()

        with self.canvas.before:
            PushMatrix()

            self.pos = Translate(*pos)
            self.rot = Rotate(0, 0, 1, 0)
            self.scale = Scale()

            Color(1, 1, 1)


        with self.canvas.after:
            PopMatrix()

        self.set_state(IDLE)

    def on_collect(self):
        pass

    def set_state(self, state):
        if state == DIE:
            self.timer = 1
        self.state = state

    def update(self, dt):
        if self.state == IDLE:
            self.rot.angle += 30 * dt
            p_pos = self.app.game_manager.player.graphics.pos
            if ((self.pos.x - p_pos.x) ** 2 + (self.pos.z - p_pos.z) ** 2 < 4
                    and (p_pos.y < self.pos.y < p_pos.y + self.app.game_manager.player.height)):
                self.set_state(DIE)

        elif self.state == DIE:
            self.timer -= dt
            if self.timer > 0:
                s = self.timer
                self.scale.x = s
                self.scale.y = s
                self.scale.z = s
            else:
                self.app.game_manager.remove_object(self)
                self.on_collect()

    def despawn(self):
        self.app.renderer.scene.remove(self.canvas)


class Health(Powerup):
    def __init__(self, app, pos):
        Powerup.__init__(self, app, pos)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/health',
                                            self.canvas,
                                            texture=None)

    def on_collect(self):
        self.app.game_manager.player.get_health()


class Fuel(Powerup):
    def __init__(self, app, pos):
        Powerup.__init__(self, app, pos)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/powerup',
                                            self.canvas,
                                            texture='apple.jpg')

    def on_collect(self):
        self.app.game_manager.player.start_powerup()


class SlowTime(Powerup):
    def __init__(self, app, pos):
        Powerup.__init__(self, app, pos)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/clock',
                                            self.canvas,
                                            texture='clock.jpg')

    def on_collect(self):
        self.app.game_manager.player.start_slow_motion()
