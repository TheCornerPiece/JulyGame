from kivy.graphics import *

import physics, util


class Platform:
    radius = 3
    height = 6

    standing = False

    def __init__(self, app, pos):
        self.app = app

        self.canvas = Canvas()

        with self.canvas.before:
            PushMatrix()

            self.pos = Translate(*pos)

        with self.canvas.after:
            PopMatrix()

        self.app.renderer.scene.add(self.canvas)
        self.app.game_manager.game_objects.add(self)
        self.collider = self.app.resource_manager.get_circle(offset=self.pos.xyz,
                                                             radius=self.radius,
                                                             height=self.height,
                                                             collision_type=physics.STATIC)
        self.collider.on_stand = self.on_stand

    def on_stand(self):
        pass

    def update(self, dt):
        pass

    def despawn(self):
        self.app.renderer.scene.remove(self.canvas)
        self.app.resource_manager.cache_circle(self.collider)


class LavaPlatform(Platform):
    radius = 5
    height = 1

    timer = 1

    def __init__(self, app, pos):
        Platform.__init__(self, app, pos)
        with self.canvas:
            self.color = Color(1, 1, 1, 1)

            self.app.graphic_data.draw_mesh('models/lava_platform',
                                            self.canvas,
                                            'metal.jpg')

    def on_stand(self):
        self.standing = True

    def set_color(self):
        self.color.rgb = 1, 1 - self.timer, 1 - self.timer

    def update(self, dt):
        if self.standing:
            if self.app.game_manager.player.collision.standing != self.collider:
                self.standing = False
            self.timer += dt
            if self.timer > .25:
                self.app.game_manager.player.damage(self.timer * 75 * dt)
            self.set_color()

        elif self.timer > 0:
            self.timer -= dt
            self.set_color()


class Trampoline(Platform):
    radius = 5
    height = 1

    timer = 1

    def __init__(self, app, pos):
        Platform.__init__(self, app, pos)
        with self.canvas:
            self.color = Color(1, 1, 1, 1)

            self.app.graphic_data.draw_mesh('models/lava_platform',
                                            self.canvas,
                                            'metal.jpg')

    def on_stand(self):
        self.app.game_manager.player.collision.dy *= -1.5


class InvisiblePlatform(Platform):
    radius = 5
    height = 1

    def __init__(self, app, pos):
        Platform.__init__(self, app, pos)
        with self.canvas:
            self.color = Color(1, 1, 1, 1)

            self.app.graphic_data.draw_mesh('models/lava_platform',
                                            self.canvas,
                                            'metal.jpg')

    def update(self, dt):
        player = self.app.game_manager.player
        dist = util.sqr_distance_between(player.graphics.pos.xyz, self.pos.xyz)
        if dist > .1:
            self.color.a = 100.0 / dist
        else:
            self.color.a = 1


class Hedge(Platform):
    radius = 3
    height = 6

    def __init__(self, app, pos):
        Platform.__init__(self, app, pos)

        with self.canvas:
            Color(1, 1, 1)
            Scale(3, 2, 3)
            self.app.graphic_data.draw_mesh('models/barrel',
                                            self.canvas,
                                            'download.jpg')

