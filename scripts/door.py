import math

import pymunk
from kivy.graphics import *

import physics


class Door:
    size = (1, 4)
    height = 7

    swing_angle = 135 / 57.3

    def __init__(self, app, pos, angle):
        self.app = app

        rads = angle / -57.3
        hw = self.size[1] * .5

        self.body = pymunk.Body()
        self.body.position = pos[::2]
        self.body.angle = rads

        static_body = self.app.physics.space.static_body

        self.collider = pymunk.Poly.create_box(self.body, self.size)
        self.collider.y = pos[1]
        self.collider.height = self.height
        self.collider.mass = .5
        self.collider.collision_type = physics.STATIC
        mask = pymunk.ShapeFilter.ALL_MASKS ^ physics.STATIC_FILTER ^ physics.DOOR_FILTER
        self.collider.filter = pymunk.ShapeFilter(categories=physics.DOOR_FILTER,
                                                  mask=mask)

        hinge_dx = math.sin(-rads) * -hw
        hinge_dy = math.cos(-rads) * -hw
        self.hinge_joint = pymunk.PivotJoint(static_body, self.body,
                                             (pos[0] + hinge_dx, pos[2] + hinge_dy))

        self.rotary_spring = pymunk.DampedRotarySpring(static_body, self.body,
                                                       -rads, 5, 5)

        min_angle = rads - self.swing_angle
        max_angle = rads + self.swing_angle

        self.rotary_limit = pymunk.RotaryLimitJoint(static_body, self.body,
                                                    min_angle, max_angle)

        self.app.physics.space.add(self.body, self.collider,
                                   self.hinge_joint, self.rotary_spring,
                                   self.rotary_limit)

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            self.pos = Translate(*pos)
            self.rot = Rotate(0, 0, 1, 0)

            self.app.graphic_data.draw_mesh('models/door',
                                            self.canvas,
                                            texture='door.png')

            PopMatrix()

    def update(self, dt):
        self.pos.x = self.body.position.x
        self.pos.z = self.body.position.y
        self.rot.angle = self.body.angle * -57.3

    def despawn(self):
        self.app.physics.space.remove(self.body, self.collider,
                                      self.hinge_joint, self.rotary_spring,
                                      self.rotary_limit)
        self.app.renderer.scene.remove(self.canvas)
