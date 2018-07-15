import os
import pickle

import building
import platform
import powerup
import elevator
import terrain
import car
import helicopter
import enemy

import gui_manager, main, util


class LevelManager:
    level_id = -1
    level_name = ''

    mode = 0
    levels = []

    def __init__(self, app):
        self.app = app

    def get_level_name(self):
        return util.get_filename(self.mode, self.level_name)

    def get_all_levels(self, mode=0):
        self.mode = mode
        if self.mode == 0:
            directory = 'levels'
        elif self.mode == 1:
            directory = 'survival'

        return [f[:-4] for f in os.listdir(directory) if f.endswith('.dat')]

    def get_levels(self):
        return self.levels

    def set_level_by_name(self, level_name):
        self.set_level(self.get_levels().index(level_name))

    def set_level(self, level_id=-1):
        if level_id == -1:
            self.level_id += 1
        elif level_id != -2:
            self.level_id = level_id

        self.app.set_paused(False)

        if self.app.state == main.GAME:
            self.app.gui_manager.set_state(gui_manager.FADE_OUT)
        else:
            self.app.gui_manager.set_state(gui_manager.IDLE)

    def load(self):
        levels = self.get_levels()
        if self.level_id > len(levels) - 1:
            self.app.set_state(main.WIN)
            self.app.score_manager.save()
        else:
            self.app.gui_manager.set_state(gui_manager.FADE_IN)

            self.app.game_manager.clear_level()

            self.level_name = levels[self.level_id]
            self.app.gui_manager.update_times(self.app.score_manager.run_scores.get(util.get_filename(self.mode,
                                                                                                      self.level_name),
                                                                                    0),
                                              self.app.score_manager.get_record(self.mode, self.level_name))

            # map_data = levels.levels[self.level_id]()
            if self.mode == 0:
                directory = 'levels'
            elif self.mode == 1:
                directory = 'survival'

            with open('{}/{}.dat'.format(directory, self.level_name), 'rb') as f:
                map_data = pickle.load(f)

            scene = self.app.renderer.scene

            model_name, texture = map_data['terrain']
            self.app.game_manager.terrain = terrain.Terrain(self.app, model_name, texture)
            scene.add(self.app.game_manager.terrain.canvas)

            self.app.game_manager.player.spawn(map_data['spawn_pos'])

            if self.mode == 0:
                self.app.game_manager.goal.spawn(map_data['goal_pos'])
            elif self.mode == 1:
                self.app.game_manager.goal.despawn()

            for data in map_data['buildings']:
                b = building.Building(self.app, building.Building.data[data[0]], data[1:4], data[4])
                # b = building.Building(self.app, building.Building.data[data[0]], data[1:4], 0)
                self.app.game_manager.game_objects.add(b)
                scene.add(b.canvas)

            for data in map_data['platforms']:
                if data[0] == 0:
                    platform.Hedge(self.app, data[1:4])
                elif data[0] == 1:
                    platform.InvisiblePlatform(self.app, data[1:4])
                elif data[0] == 2:
                    platform.LavaPlatform(self.app, data[1:4])
                elif data[0] == 3:
                    platform.Trampoline(self.app, data[1:4])

            for data in map_data['elevators']:
                e = elevator.Elevator(self.app, data[1:4], data[4])
                self.app.game_manager.game_objects.add(e)  # spawn later
                scene.add(e.canvas)

            for data in map_data['powerups']:
                if data[0] == 0:
                    e = powerup.Fuel(self.app, data[1:4])
                    self.app.game_manager.game_objects.add(e)  # spawn later
                    scene.add(e.canvas)
                elif data[0] == 1:
                    e = powerup.Health(self.app, data[1:4])
                    self.app.game_manager.game_objects.add(e)  # spawn later
                    scene.add(e.canvas)
                elif data[0] == 2:
                    e = powerup.SlowTime(self.app, data[1:4])
                    self.app.game_manager.game_objects.add(e)  # spawn later
                    scene.add(e.canvas)

            for data in map_data['vehicles']:
                if data[0] == 0:
                    v = car.Car(self.app)
                elif data[0] == 1:
                    v = helicopter.Helicopter(self.app)
                v.spawn(data[1:4])

            for data in map_data['enemies']:
                if data[0] == 0:
                    enemy.Turret(self.app, data[1:4])
                elif data[0] == 1:
                    enemy.Bee(self.app, data[1:4])
                elif data[0] == 2:
                    enemy.BowlSpawner(self.app, data[1:4])
                elif data[0] == 3:
                    enemy.InvisibleEnemy(self.app, data[1:4])

            self.app.game_manager.set_state(self.mode)
