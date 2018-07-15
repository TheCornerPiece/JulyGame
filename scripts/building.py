import math
import pymunk

from kivy.graphics import *

import physics, door, stairs


class Building:
    data = [{'mesh_name': 'models/test_building',
             'texture': 'wood.jpg',
             'colliders': [[[8, 8, 7.2, 8, 7.2, -8, 8, -8], 7.1, 8.8],
                           [[8, -1.9, 7.2, -1.9, 7.2, -8, 8, -8], 0, 15.9],
                           [[8, 1.9, 7.2, 1.9, 7.2, 8, 8, 8], 0, 15.9],
                           [[-8, -8, -8, -7.5, 7.2, -8, 8, -8], 0, 15.9],
                           [[-8, 8, -8, 7.5, 7.2, 8, 8, 8], 0, 15.9],
                           [[-8, 8, -8, -8, -7.6, -8, -7.6, 8], 0, 15.9],
                           [[-8, -8, 8, -8, 8, 8, -8, 8], 15.5, .5],
                           [[-8, -8, 8, -8, 8, 8, -8, 8], -.5, .5],
                           ],
             'doors': [[7.5, 0.0, 0.0]],
             'stairs': []},
            {'mesh_name': 'models/test_building',
             'texture': 'wood.jpg',
             'colliders': [[[8, 8, 7.2, 8, 7.2, -8, 8, -8], 7.1, 8.9],
                           [[8, -1.9, 7.2, -1.9, 7.2, -8, 8, -8], 0, 7.1],
                           [[8, 1.9, 7.2, 1.9, 7.2, 8, 8, 8], 0, 7.1],
                           [[-8, -8, -8, -7.5, 7.2, -8, 8, -8], 0, 16],
                           [[-8, 8, -8, 7.5, 7.2, 8, 8, 8], 0, 16],
                           [[-8, 8, -8, -8, -7.6, -8, -7.6, 8], 0, 16],
                           [[-8, -8, 8, -8, 8, 8, -8, 8], 15.5, .5],
                           [[-8, -8, 8, -8, 8, 8, -8, 8], -.5, .5],
                           ],
             'doors': [[7.5, 0.0, 0.0]],
             'stairs': []},
            ]

    def __init__(self, app, data, pos=(0, 0, 0), angle=0):
        self.app = app

        rads = angle / 57.3
        cos = math.cos(rads)
        sin = math.sin(rads)

        transform = pymunk.Transform(a=cos, b=-sin,
                                     c=sin, d=cos,
                                     tx=pos[0], ty=pos[2])

        f = pymunk.ShapeFilter(categories=physics.STATIC_FILTER)

        self.colliders = []
        for c in data['colliders']:
            vertices = zip(c[0][::2], c[0][1::2])
            collider = pymunk.Poly(self.app.physics.space.static_body,
                                   vertices=vertices,
                                   transform=transform)
            collider.y = pos[1] + c[1]
            collider.height = c[2]
            collider.collision_type = physics.STATIC
            collider.filter = f
            self.app.physics.space.add(collider)
            self.colliders.append(collider)

        for x, y, z in data['stairs']:
            stairs_x = pos[0] + (cos * x + sin * z)
            stairs_y = pos[1] + y
            stairs_z = pos[2] + (-sin * x + cos * z)
            d = stairs.Staircase(self.app,
                                 pos=(stairs_x, stairs_y, stairs_z),
                                 angle=angle)
            self.app.game_manager.game_objects.add(d)
            self.app.renderer.scene.add(d.canvas)

        self.doors = []
        for x, y, z in data['doors']:
            door_x = pos[0] + (cos * x + sin * z)
            door_y = pos[1] + y
            door_z = pos[2] + (-sin * x + cos * z)
            d = door.Door(self.app,
                          pos=(door_x, door_y, door_z),
                          angle=angle)
            self.doors.append(d)
            self.app.game_manager.game_objects.add(d)
            self.app.renderer.scene.add(d.canvas)

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            Color(1, 1, 1)
            self.pos = Translate(*pos)
            Rotate(angle, 0, 1, 0)

            self.app.graphic_data.draw_mesh(data['mesh_name'],
                                            self.canvas,
                                            texture=data['texture'])

            PopMatrix()

    def update(self, dt):
        pass

    def despawn(self):
        self.app.physics.space.remove(self.colliders)
        self.app.renderer.scene.remove(self.canvas)
