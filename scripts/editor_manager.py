import os
import pickle

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import *

import main


class EditorButton(Button):
    def __init__(self, **kwargs):
        Button.__init__(self, **kwargs)

    def on_release(self, *args):
        App.get_running_app().editor_manager.set_selection(self.text)


class EditorObject(Widget):
    def __init__(self, obj_type, first_attr=0, y_pos=0, angle=0, **kwargs):
        self.obj_type = obj_type
        self.first_attr = first_attr
        self.y_pos = y_pos
        self.angle = angle
        Widget.__init__(self, **kwargs)

    def on_touch_move(self, touch):
        self.x += touch.dx
        self.y += touch.dy


def is_number(string):
    return string.text.replace('.', '').isdigit()


class EditorManager(Widget):
    default_data = {'spawn_pos': [0, 0, 0],
                    'goal_pos': [0, 0, 0],
                    'terrain': ['models/Level1', 'dirt.jpg'],
                    'buildings': [],
                    'platforms': [],
                    'powerups': [],
                    'enemies': [],
                    'elevators': [],
                    'vehicles': []}

    level_name = 'default'
    mode = 0

    def __init__(self, app):
        Widget.__init__(self)
        with self.canvas:
            PushMatrix()

            self.cam_pos = Translate()
            self.scale = Scale(5)

        with self.canvas.after:
            PopMatrix()

        self.app = app
        self.selection = None

        self.spawn_object = EditorObject('spawn_pos',
                                         color=(1, 0, 0, 1),
                                         size=(1, 1))
        self.goal_object = EditorObject('goal_pos',
                                        color=(1, 0, 0, 1),
                                        size=(1, 1))

        self.add_widget(self.spawn_object)
        self.add_widget(self.goal_object)

        self.objects = set()

        self.selection_label = self.app.root.ids['selection_label']
        self.first_attr = self.app.root.ids['first_attr']
        self.y_pos = self.app.root.ids['y_pos']
        self.angle = self.app.root.ids['angle']

    def set_level_name(self, name):
        self.level_name = name
        self.load()

    def get_world_pos(self, x, y):
        return (x - self.cam_pos.x) / self.scale.x, (y - self.cam_pos.y) / self.scale.y

    def clear(self):
        for o in self.objects:
            self.remove_widget(o)
        self.objects.clear()

    def set_mode(self, mode):
        self.mode = mode

    def play_level(self):
        self.app.level_manager.mode = self.mode
        self.app.level_manager.levels = [self.level_name]
        self.app.set_state(main.GAME)

    def save(self):
        data = {}

        for k, v in self.default_data.iteritems():
            if isinstance(v, list):
                data[k] = list(v)
            else:
                data[k] = v

        if self.mode == 0:
            directory = 'levels'
        else:
            directory = 'survival'

        data['spawn_pos'] = [self.spawn_object.x,
                             self.spawn_object.y_pos,
                             self.spawn_object.y]
        data['goal_pos'] = [self.goal_object.x,
                            self.goal_object.y_pos,
                            self.goal_object.y]
        for o in self.objects:
            data[o.obj_type].append((o.first_attr, o.x, o.y_pos, o.y, o.angle))

        with open('{}/{}.dat'.format(directory, self.level_name), 'wb') as f:
            pickle.dump(data, f)

    def load(self):
        if self.mode == 0:
            directory = 'levels'
        else:
            directory = 'survival'

        filename = '{}/{}.dat'.format(directory, self.level_name)
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)

            self.clear()

            x, y, z = data['spawn_pos']
            self.add_object('spawn_pos', 0, y, (x, z), 0)

            x, y, z = data['goal_pos']
            self.add_object('goal_pos', 0, y, (x, z), 0)

            for obj_type, datas in data.iteritems():
                if obj_type not in ('terrain', 'spawn_pos', 'goal_pos'):
                    for f, x, y, z, a in datas:
                        self.add_object(obj_type, f, y, (x, z), a)
        else:
            self.clear()

    def set_selection(self, button_text):
        self.selection = button_text
        self.selection_label.text = self.selection

    def add_object(self, obj_type, first_attr, y_pos, pos, angle):
        if obj_type == 'spawn_pos':
            self.spawn_object.pos = pos
            self.spawn_object.y_pos = y_pos
        elif obj_type == 'goal_pos':
            self.goal_object.pos = pos
            self.goal_object.y_pos = y_pos
        else:
            obj = EditorObject(obj_type,
                               first_attr=first_attr,
                               y_pos=y_pos, angle=angle,
                               pos=pos)
            if obj_type == 'buildings':
                obj.size = 16, 16
            else:
                obj.size = 3, 3

            self.objects.add(obj)
            self.add_widget(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)
        self.remove_widget(obj)

    def on_touch_down(self, touch):
        if touch.button == 'left':
            if self.selection:
                if is_number(self.y_pos):
                    y_pos = float(self.y_pos.text)
                else:
                    y_pos = 0
                if is_number(self.first_attr):
                    first_attr = float(self.first_attr.text)
                else:
                    first_attr = 0
                if is_number(self.angle):
                    angle = float(self.angle.text)
                else:
                    angle = 0

                pos = self.get_world_pos(*touch.pos)

                self.add_object(self.selection, first_attr, y_pos, pos, angle)

        elif touch.button == 'right':
            pos = self.get_world_pos(*touch.pos)

            for o in self.objects:
                hw = o.width * .5
                hh = o.height * .5
                if o.x - hw < pos[0] < o.x + hw and o.y - hh < pos[1] < o.y + hh:
                    self.remove_object(o)
                    break

    def on_touch_move(self, touch):
        if touch.button == 'right':
            self.cam_pos.x += touch.dx
            self.cam_pos.y += touch.dy

    def on_touch_up(self, touch):
        pass
