MENU, GAME, EDITOR, WIN, LEVELS, MPLOBBY = xrange(6)

if __name__ == '__main__':
    from kivy.support import install_twisted_reactor

    install_twisted_reactor()

    from kivy.config import Config

    Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

    from kivy.app import App
    from kivy.clock import Clock

    from scripts import (game_manager,
                         renderer,
                         graphic_data,
                         input_manager,
                         resource_manager,
                         physics,
                         level_manager,
                         gui_manager,
                         network_manager,
                         editor_manager,
                         score_manager)


    class Application(App):
        target_dt = 1 / 45.0
        max_dt = 1 / 20.0

        time_scale = 1.0

        last_state = 0
        state = -1
        paused = False

        def build(self):
            self.score_manager = score_manager.ScoreManager()
            self.editor_manager = editor_manager.EditorManager(self)
            self.network_manager = network_manager.NetworkManager(self)
            self.gui_manager = gui_manager.GuiManager(self)
            self.physics = physics.PhysicsManager(self)
            self.graphic_data = graphic_data.GraphicData()
            self.input_manager = input_manager.InputManager(self)
            self.resource_manager = resource_manager.ResourceManager(self)
            self.renderer = renderer.Renderer(self)
            self.game_manager = game_manager.GameManager(self)
            self.level_manager = level_manager.LevelManager(self)


            game_screen = self.root.get_screen('game')
            game_screen.add_widget(self.input_manager)
            game_screen.add_widget(self.renderer, 10)

            editor_screen = self.root.get_screen('editor')
            editor_screen.add_widget(self.editor_manager, 10)

            self.set_state(MENU)
            Clock.schedule_interval(self.update, self.target_dt)

        def return_to_entry(self):
            self.set_state(self.last_state)

        def set_state(self, state):
            if state == GAME:
                self.paused = False
                self.gui_manager.set_paused(False)
                self.root.current = 'game'
                self.score_manager.load()
                self.gui_manager.reset_timer()
                if self.state == MENU:
                    self.level_manager.levels = self.level_manager.get_all_levels(0)
                self.level_manager.set_level(0)
                self.level_manager.load()

            elif state == MPLOBBY:
                self.network_manager.connect_to_server()
                self.root.current = 'lobby'
                self.last_state = MENU
            elif state == MENU:
                self.network_manager.disconnect()
                self.root.current = 'menu'
                self.last_state = state
            elif state == EDITOR:
                self.root.current = 'editor'
                self.last_state = state
            elif state == WIN:
                self.root.current = 'win'
                self.gui_manager.display_final_time()
            elif state == LEVELS:
                self.root.current = 'levels'
                self.score_manager.load()
                self.gui_manager.display_levels(self.level_manager.mode)
                self.last_state = state
            self.state = state

        def start_multiplayer(self):
            self.network_manager.send_message('v;')
            self.level_manager.levels = self.level_manager.get_all_levels()
            self.set_state(GAME)

        def set_paused(self, value=True):
            self.paused = value
            self.gui_manager.set_paused(self.paused)

        def on_esc(self):
            if self.state == GAME:
                self.set_paused(not self.paused)
            elif self.state == MENU:
                self.stop()

        def update(self, real_dt):
            if real_dt > self.max_dt:
                real_dt = self.max_dt
                dt = real_dt
            else:
                dt = real_dt * self.time_scale

            if self.state == GAME:
                if not self.paused:
                    self.game_manager.update(dt)
                    self.physics.update(dt)
                    self.gui_manager.update(dt)

                self.renderer.update(real_dt)


    Application().run()
