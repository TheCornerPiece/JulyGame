import pymunk

from kivy.graphics import *

import vehicle, util


class Helicopter(vehicle.Vehicle):
    vertices = util.get_rect(6, 4)
    height = 5.5

    accel_force = -100.0
    turn_force = 100
    idle_turn_factor = .3
    max_speed = 20
    min_speed = -max_speed * .5
    max_angular_velocity = 2

    max_y_vel = 10

    seat_offset = -.1

    side_friction = 3
    friction_speed = 15
    stop_speed = .1

    a_damping = .4

    prop_vel = 0

    def __init__(self, app):
        vehicle.Vehicle.__init__(self, app)

        with self.canvas:
            self.rot = Rotate(0, 0, 1, 0)
            self.pitch = Rotate(0, 0, 0, 1)
            self.roll = Rotate(0, 1, 0, 0)

            self.app.graphic_data.draw_mesh('models/helicopter',
                                            self.canvas,
                                            texture='metal.jpg')

            PushMatrix()
            self.prop_rot = Rotate(0, 0, 1, 0)

            Translate(0, 4, 0)
            self.app.graphic_data.draw_mesh('models/propellers',
                                            self.canvas,
                                            texture=None)
            PopMatrix()

    def velocity_func(self, body, gravity, damping, dt):
        if self.collision.standing:
            body.velocity *= .5
            body.angular_velocity *= 0
        else:
            if self.input_vector:
                if abs(body.angular_velocity) > self.max_angular_velocity:
                    body.angular_velocity = self.max_angular_velocity * cmp(body.angular_velocity, 0)
                self.local_vel = pymunk.Vec2d(body.velocity).rotated(-body.angle)
                self.local_vel.y *= (1 - self.side_friction * dt)
                self.local_vel.x = min(self.max_speed, max(self.min_speed, self.local_vel.x))
                body.velocity = self.local_vel.rotated(body.angle)
            else:
                friction = self.friction_speed * dt
                if self.local_vel.x < friction:
                    body.velocity *= .8
                    body.angular_velocity *= 0
                else:
                    body.velocity -= body.velocity.normalized() * friction
        body.angular_velocity *= 1 - (.9 * dt)

    def move(self, input_vector, dt):
        if not self.collision.standing:
            self.local_vel = pymunk.Vec2d(self.collision.body.velocity).rotated(-self.collision.body.angle)

            self.input_vector = input_vector
            self.collision.body.apply_impulse_at_local_point((self.input_vector[1] * self.accel_force * dt,
                                                              self.input_vector[0] * self.turn_force * dt),
                                                             (self.wheel_offset, 0))

    def update(self, dt):
        if self.turned_on:
            accel = (self.throttle_up - self.throttle_down)

            target_vel = accel * 200 + 700
            self.prop_vel += cmp(target_vel, self.prop_vel) * 500 * dt

            self.prop_rot.angle += self.prop_vel * dt

        elif self.prop_vel > 0:
            self.prop_vel -= 200 * dt
            if self.prop_vel < 0:
                self.prop_vel = 0
            else:
                self.prop_rot.angle += self.prop_vel * dt

        self.rot.angle = self.collision.body.angle * -57.3

        if self.collision.standing:
            if self.collision.dy > 0:
                self.collision.standing = None
            self.pitch.angle = 0
            self.roll.angle = 0
        else:
            self.pitch.angle += (self.input_vector[1] * 20 - self.pitch.angle) * .05
            self.roll.angle += (self.input_vector[0] * 20 - self.roll.angle) * .05

        self.collision.dy += (self.throttle_up - self.throttle_down - .2) * 30 * dt
        if abs(self.collision.dy) > self.max_y_vel:
            self.collision.dy = cmp(self.collision.dy, 0) * self.max_y_vel

        vehicle.Vehicle.update(self, dt)
