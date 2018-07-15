from kivy.graphics import *

import util, character, gui_manager

IDLE, COLLECTED = xrange(2)


class Goal:
    state = -1
    enabled = True

    def __init__(self, app):
        self.app = app

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            Color(1, 1, 1, 1)

            self.pos = Translate()
            self.rot = Rotate(0, 0, 1, 0)

            self.app.graphic_data.draw_mesh('models/chocolate',
                                            self.canvas,
                                            'chocolate.jpg')

            PopMatrix()

        self.set_state(IDLE)

    def spawn(self, pos):
        self.pos.xyz = pos
        self.set_state(IDLE)
        if not self.enabled:
            self.app.renderer.scene.add(self.canvas)
        self.enabled = True

    def despawn(self):
        if self.enabled:
            self.app.renderer.scene.remove(self.canvas)
        self.enabled = False

    def set_state(self, state):
        if state == COLLECTED:
            self.app.level_manager.set_level()
        self.state = state

    def update(self, dt):
        player = self.app.game_manager.player

        if self.state == IDLE:
            self.rot.angle += dt * 90
            d = util.sqr_distance_between(self.pos.xyz[::2], player.graphics.pos.xyz[::2])
            self.app.gui_manager.set_goal_distance(d + (self.pos.y - player.graphics.pos.y) ** 2)
            if player.state not in (character.DRIVING, character.DIE):
                if d < 9:
                    if player.graphics.pos.y - 1 < self.pos.y < player.graphics.pos.y + player.height + 1:
                        # self.app.game_manager.game_objects.remove(self)
                        # self.app.renderer.scene.remove(self.canvas)
                        player.set_state(character.WIN)
                        self.set_state(COLLECTED)

        elif self.state == COLLECTED:
            self.pos.xyz = player.get_hand_pos(1)
            self.rot.angle = player.graphics.rot.angle