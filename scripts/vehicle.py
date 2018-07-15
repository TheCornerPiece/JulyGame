import pymunk

from kivy.graphics import *

import physics, dynamic_object


class Vehicle:
    vertices = []
    height = 4.5

    accel_force = -100.0
    turn_force = 5
    idle_turn_factor = .3
    max_speed = 30
    min_speed = -max_speed * .3
    max_angular_velocity = 4

    elasticity = .4

    seat_offset = 1

    wheel_offset = 1.9

    side_friction = 3
    friction_speed = 15
    stop_speed = .1

    a_damping = .4

    turned_on = False

    def __init__(self, app):
        self.app = app
        self.collision = dynamic_object.DynamicObject(self.app)
        self.collision.body.velocity_func = self.velocity_func
        self.collision.spawn_collider(self.app, pymunk.Poly(None, self.vertices),
                                      0, self.height)

        self.canvas = Canvas()
        with self.canvas.before:
            PushMatrix()

            self.pos = Translate()
            self.rot = Rotate(0, 0, 1, 0)

        with self.canvas.after:
            PopMatrix()

        self.throttle_up = 0
        self.throttle_down = 0
        self.input_vector = [0, 0]
        self.local_vel = pymunk.Vec2d()

    def velocity_func(self, body, gravity, damping, dt):
        if self.throttle_down - self.throttle_up:
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
        body.angular_velocity *= 1 - (self.a_damping * self.local_vel.x) * dt

    def spawn(self, pos):
        self.pos.y = pos[1]
        self.collision.spawn(pos)

        self.app.renderer.scene.add(self.canvas)
        self.app.game_manager.game_objects.add(self)
        self.app.game_manager.vehicles.add(self)

    def move(self, input_vector, dt):
        pass

    def despawn(self):
        self.app.renderer.scene.remove(self.canvas)
        self.collision.despawn()

    def turn_off(self):
        self.turned_on = False
        self.input_vector = [0, 0]
        self.throttle_down = 0
        self.throttle_up = 0

    def update(self, dt):
        self.collision.move_y(dt)
        self.collision.update(dt)
        self.pos.xyz = self.collision.get_pos()

    def left_trigger_down(self):
        self.throttle_down = 1
        self.turned_on = True

    def left_trigger_up(self):
        self.throttle_down = 0

    def right_trigger_down(self):
        self.throttle_up = 1
        self.turned_on = True

    def right_trigger_up(self):
        self.throttle_up = 0
