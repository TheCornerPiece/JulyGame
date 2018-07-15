import pymunk

from kivy.graphics import *

import vehicle, util


class Car(vehicle.Vehicle):
    vertices = util.get_rect(6, 4)
    height = 4.5

    accel_force = -100.0
    turn_force = 3
    idle_turn_factor = .3
    max_speed = 40
    min_speed = -max_speed * .3
    max_angular_velocity = 4

    seat_offset = 1

    wheel_offset = 2

    side_friction = 3
    friction_speed = 20
    stop_speed = .1

    a_damping = .4

    timer = 0

    def __init__(self, app):
        vehicle.Vehicle.__init__(self, app)

        wheel_tex = 'wheel.jpg'

        self.wheel_rots = set()

        with self.canvas:
            self.rot = Rotate(0, 0, 1, 0)
            Translate(0, 1.5, 0)

            self.app.graphic_data.draw_mesh('models/car',
                                            self.canvas,
                                            texture='metal.jpg')

            axel_width = 2.5

            PushMatrix()
            Translate(2, 0, 0)

            PushMatrix()
            Translate(0, 0, -axel_width)

            self.fl_rot = Rotate(0, 0, 1, 0)
            self.wheel_rots.add(Rotate(0, 0, 0, 1))
            self.app.graphic_data.draw_mesh('models/wheel',
                                            self.canvas,
                                            wheel_tex)
            PopMatrix()

            PushMatrix()
            Translate(0, 0, axel_width)
            self.fr_rot = Rotate(0, 0, 1, 0)
            self.wheel_rots.add(Rotate(0, 0, 0, 1))
            self.app.graphic_data.draw_mesh('models/wheel',
                                            self.canvas,
                                            wheel_tex)
            PopMatrix()
            PopMatrix()

            PushMatrix()
            Translate(-2, 0, 0)
            self.wheel_rots.add(Rotate(0, 0, 0, 1))

            PushMatrix()
            Translate(0, 0, -axel_width)
            self.app.graphic_data.draw_mesh('models/wheel',
                                            self.canvas,
                                            wheel_tex)
            PopMatrix()

            PushMatrix()
            Translate(0, 0, axel_width)
            self.app.graphic_data.draw_mesh('models/wheel',
                                            self.canvas,
                                            wheel_tex)
            PopMatrix()
            PopMatrix()

    def move(self, input_vector, dt):
        self.input_vector = list(input_vector)
        accel = self.throttle_down - self.throttle_up

        self.local_vel = pymunk.Vec2d(self.collision.body.velocity).rotated(-self.collision.body.angle)

        if self.local_vel.x:
            mag = self.local_vel.x
            if not accel:
                mag *= self.idle_turn_factor
            self.input_vector[0] *= mag
        else:
            self.input_vector[0] = 0

        self.collision.body.apply_impulse_at_local_point((accel * self.accel_force * dt,
                                                          self.input_vector[0] * self.turn_force * dt),
                                                         (self.wheel_offset, 0))

    def update(self, dt):
        accel = (self.throttle_down - self.throttle_up)

        target_angle = self.input_vector[0] * accel

        da = accel * 1000 * dt
        for r in self.wheel_rots:
            r.angle += da

        da = (target_angle - self.fr_rot.angle) * .2

        self.fr_rot.angle += da
        self.fl_rot.angle += da

        self.rot.angle = self.collision.body.angle * -57.3

        if not self.collision.standing:
            self.collision.dy -= 10 * dt
            self.collision.move_y(dt)

        vehicle.Vehicle.update(self, dt)
