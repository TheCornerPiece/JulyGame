import util

import main

from kivy.uix.gridlayout import GridLayout

FADE_IN, IDLE, FADE_OUT = xrange(3)


class LevelResult(GridLayout):
    def __init__(self, level_name, run_time, best_time, color):
        GridLayout.__init__(self, color=color)

        self.ids['level_name'].text = level_name
        self.ids['run_time'].text = util.format_time(run_time)
        self.ids['best_time'].text = util.format_time(best_time)


class LevelSelection(GridLayout):
    def __init__(self, app, level_name, best_time, mode, color):
        self.app = app
        GridLayout.__init__(self, color=color)

        self.mode = mode

        self.ids['level_name'].text = level_name
        self.ids['best_time'].text = util.format_time(best_time)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            level_name = self.ids['level_name'].text
            if self.app.gui_manager.play_button.state == 'down':
                self.app.level_manager.mode = self.mode
                self.app.level_manager.levels = [level_name]
                self.app.set_state(main.GAME)
            else:
                self.app.set_state(main.EDITOR)
                self.app.editor_manager.mode = self.mode
                self.app.editor_manager.set_level_name(level_name)


class GuiManager:
    damage_time = 1 / .5

    state = -1
    timer = 0

    def __init__(self, app):
        self.app = app

        self.fade = self.app.root.ids['fade']
        self.health_bar = self.app.root.ids['health_bar']
        self.powerup_bar = self.app.root.ids['powerup_bar']
        self.paused_label = self.app.root.ids['paused_label']
        self.restart_button = self.app.root.ids['restart_button']
        self.menu_button = self.app.root.ids['menu_button']
        self.time_label = self.app.root.ids['time_label']
        self.level_record_label = self.app.root.ids['level_record_label']
        self.total_time_label = self.app.root.ids['total_time_label']
        self.record_grid = self.app.root.ids['record_grid']
        self.level_grid = self.app.root.ids['level_grid']
        self.win_label = self.app.root.ids['win_label']
        self.play_button = self.app.root.ids['play_button']
        self.goal_indicator = self.app.root.ids['goal_indicator']

        self.health_bar.color = 1, 0, 0, 1
        self.powerup_bar.color = 0, 0, 1, 1

        self.damage_timer = 0
        self.powerup_timer = 0

        self.set_powerup(0)

        self.set_state(FADE_IN)

    def set_paused(self, value=True):
        if value:
            self.paused_label.opacity = 1
            self.restart_button.opacity = 1
            self.menu_button.opacity = 1
        else:
            self.paused_label.opacity = 0
            self.restart_button.opacity = 0
            self.menu_button.opacity = 0

    def display_levels(self, mode=0):
        self.level_grid.clear_widgets()
        for i, level_name in enumerate(self.app.level_manager.get_all_levels(mode)):
            if i % 2:
                color = .2, .2, .2, 1
            else:
                color = .2, .2, .4, 1

            best_time = self.app.score_manager.get_record(mode, level_name)
            selection = LevelSelection(self.app, level_name, best_time, mode, color)
            self.level_grid.add_widget(selection)

    def update_times(self, total_time, record_time):
        if total_time:
            self.total_time_label.text = '+{}'.format(util.format_time(total_time))
        else:
            self.total_time_label.text = ''
        self.level_record_label.text = util.format_time(record_time)

    def set_state(self, state):
        self.state = state

    def set_health(self, amt):
        self.health_bar.size_hint_x = .25 * (amt / 100.0)
        self.damage_timer = 1

    def set_goal_distance(self, d):
        if d < 30**2:
            self.goal_indicator.source = 'textures/goal_close.png'
        elif d < 60**2:
            self.goal_indicator.source = 'textures/goal_med.png'
        else:
            self.goal_indicator.source = 'textures/goal_far.png'

    def set_powerup(self, amt):
        if amt == 0:
            self.powerup_bar.size_hint_x = 0
            self.powerup_timer = 1
        else:
            self.powerup_bar.size_hint_x = .25 * amt

    def display_final_time(self):
        self.record_grid.clear_widgets()

        l = sorted(self.app.score_manager.run_scores.iteritems(), key=lambda i: i[0])

        total_time = 0
        for i, data in enumerate(l):
            level_name, score = data

            if i % 2:
                color = .2, .2, .2, 1
            else:
                color = .2, .2, .4, 1

            result = LevelResult(level_name, score,
                                 self.app.score_manager.best_scores.get(level_name, -1),
                                 color)
            self.record_grid.add_widget(result)

            total_time += score

        self.win_label.text = util.format_time(total_time)

    def reset_timer(self):
        self.timer = 0

    def update(self, dt):
        if self.state == FADE_OUT:
            self.fade.opacity += dt * .4
            if self.fade.opacity > 1:
                self.fade.opacity = 1
                self.set_state(IDLE)

                self.app.score_manager.log_score(self.app.level_manager.get_level_name(), round(self.timer, 3))
                self.reset_timer()
                self.app.level_manager.load()
        else:
            self.timer += dt
            self.time_label.text = util.format_time(self.timer)

            if self.state == IDLE:
                if self.damage_timer > 0:
                    self.damage_timer -= dt * 2 * self.damage_time
                    if self.damage_timer < 0:
                        self.damage_timer = 0
                    d = self.damage_timer
                    self.health_bar.color = 1, d, d, 1

                if self.powerup_bar.size_hint_x > 0:
                    self.powerup_timer -= dt
                    if self.powerup_timer < 0:
                        self.powerup_timer += 1

                    d = self.powerup_timer
                    self.powerup_bar.color = d, d, 1, 1

            elif self.state == FADE_IN:
                self.fade.opacity -= dt * .5
                if self.fade.opacity < 0:
                    self.fade.opacity = 0
                    self.set_state(IDLE)


