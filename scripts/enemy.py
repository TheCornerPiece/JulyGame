import math
import pymunk

from kivy.graphics import *

import health_bar, dynamic_object, util, physics


class Enemy:
    max_health = 100.0
    damage_timer = 0

    def __init__(self, app, pos, health_offset=0):
        self.app = app

        self.canvas = Canvas()
        with self.canvas.before:
            PushMatrix()

            self.color = Color(1, 1, 1, 1)

            self.pos = Translate(*pos)
            self.rot = Rotate(0, 0, 1, 0)

        with self.canvas.after:
            PopMatrix()

        if health_offset is False:
            self.health_bar = None
        else:
            self.health_offset = health_offset
            self.health_bar = health_bar.HealthBar(self.app)
            self.app.renderer.scene.add(self.health_bar.canvas)

        self.spawn_collider()

        self.app.renderer.scene.add(self.canvas)
        self.app.game_manager.game_objects.add(self)
        self.app.game_manager.enemies.add(self)

        self.health = self.max_health

    def spawn_collider(self):
        pass

    def despawn(self):
        self.app.game_manager.enemies.remove(self)
        self.app.renderer.scene.remove(self.canvas)
        if self.health_bar:
            self.health_bar.despawn()

    def damage(self, amt):
        self.damage_timer = 1
        self.health -= amt
        if self.health <= 0:
            self.app.game_manager.remove_object(self)
            self.app.game_manager.killed_enemy()
        elif self.health_bar:
            self.health_bar.scale.x = self.health / self.max_health

    def update(self, dt):
        if self.damage_timer > 0:
            self.damage_timer -= dt * 2

            if self.damage_timer > 0:
                i = 1 - self.damage_timer
                self.color.rgb = (1, i, i)
            else:
                self.color.rgb = 1, 1, 1

        if self.health_bar:
            self.health_bar.pos.xyz = (self.pos.x,
                                       self.pos.y + self.health_offset,
                                       self.pos.z)
            self.health_bar.update(dt)


CHASING, COOLDOWN = xrange(2)


class Bee(Enemy):
    radius = 1
    sting_radius = 1.95
    height = 3
    speed = .4
    vertical_speed = 7

    timer = 0
    cooldown_timer = 0

    max_health = 60.0

    def __init__(self, app, pos):
        Enemy.__init__(self, app, pos, 3)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/bee',
                                            self.canvas,
                                            'bee.jpg')

            PushMatrix()

            Translate(0, 1, 0)
            self.wing_rot = Rotate(0, 0, 0, 1)

            self.app.graphic_data.draw_mesh('models/bee_wing',
                                            self.canvas,
                                            'bee_wing.jpg')

            Scale(-1, 1, 1)

            self.app.graphic_data.draw_mesh('models/bee_wing',
                                            self.canvas,
                                            'bee_wing.jpg')

            PopMatrix()

    def spawn_collider(self):
        self.collision = dynamic_object.DynamicObject(self.app)
        self.collision.spawn_collider(self.app, pymunk.Circle(None, self.radius),
                                      y=self.pos.y, height=self.height)
        self.collision.collider.damage_object = self

        self.collision.spawn(self.pos.xyz)

    def despawn(self):
        self.collision.despawn()
        Enemy.despawn(self)

    def update(self, dt):
        if self.cooldown_timer < 0:
            player_pos = self.app.game_manager.player.graphics.pos
            dx = player_pos.x - self.pos.x
            dy = (player_pos.y + 2) - self.pos.y
            dz = player_pos.z - self.pos.z

            mag = ((dx ** 2) + (dz ** 2)) ** .5
            if mag < self.sting_radius and abs(dy) < 3:
                self.app.game_manager.player.damage(25)
                self.cooldown_timer = 1

            speed = self.speed / mag

            self.collision.body.apply_impulse_at_world_point((dx * speed, dz * speed))
            self.collision.dy = cmp(dy, 0) * self.vertical_speed
            self.collision.move_y(dt)

            self.rot.angle = math.atan2(dx, dz) * 57.3

        else:
            self.cooldown_timer -= dt

        Enemy.update(self, dt)

        self.pos.xyz = self.collision.get_pos()

        self.timer += dt
        self.wing_rot.angle = util.loop_time(self.timer, .1, True) * 45


class BowlSpawner(Enemy):
    timer = 0
    speed = 5

    def __init__(self, app, pos):
        Enemy.__init__(self, app, pos, False)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/bowl_spawner',
                                            self.canvas,
                                            'metal.jpg')

    def update(self, dt):
        player_pos = self.app.game_manager.player.graphics.pos
        dx = (player_pos.x - self.pos.x)
        dz = (player_pos.z - self.pos.z)

        if not (dx == dz == 0):
            mag = ((dx ** 2) + (dz ** 2)) ** .5
            speed = self.speed
            if speed > mag:
                self.pos.x = player_pos.x
                self.pos.z = player_pos.z
            else:
                self.pos.x += dx * speed * dt / mag
                self.pos.z += dz * speed * dt / mag

        self.timer -= dt * .3
        self.rot.angle = self.timer * 1440
        if self.timer < 0 and player_pos.y < self.pos.y:
            self.timer = 1
            Bowl(self.app, self.pos.xyz)


class Bowl(Enemy):
    radius = 1
    height = 1

    def __init__(self, app, pos):
        Enemy.__init__(self, app, pos, False)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/bowl',
                                            self.canvas,
                                            'bowl.jpg')

    def spawn_collider(self):
        self.collision = dynamic_object.DynamicObject(self.app, self)

        self.collision.spawn_collider(self.app, pymunk.Circle(None, self.radius),
                                      y=self.pos.y, height=self.height)
        self.collision.spawn(self.pos.xyz)

    def set_standing(self, c, shape=True):
        if self.collision.dy < -30:
            if shape and c is self.app.game_manager.player.collision.collider:
                self.app.game_manager.player.damage(50)

    def removed_standing(self):
        pass

    def despawn(self):
        self.collision.despawn()
        Enemy.despawn(self)

    def update(self, dt):
        self.collision.dy -= 30 * dt
        self.collision.move_y(dt)

        self.pos.xyz = self.collision.get_pos()


class InvisibleEnemy(Enemy):
    gravity = 25

    speed = .5

    radius = 1
    height = 6

    step_height = 1.5

    max_health = 75.0

    def __init__(self, app, pos):
        Enemy.__init__(self, app, pos, 6)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/enemy',
                                            self.canvas,
                                            'robot_texture.jpg')

        self.set_pos(pos)

    def spawn_collider(self):
        self.body = pymunk.Body()
        self.body.velocity_func = self.velocity_func

        self.collider = pymunk.Circle(self.body, self.radius)
        self.collider.damage_object = self
        self.collider.parent = self
        self.collider.height = self.height
        self.collider.mass = 1
        self.collider.collision_type = physics.DYNAMIC
        self.app.physics.space.add(self.body, self.collider)

    def velocity_func(self, body, gravity, damping, dt):
        return pymunk.Body.update_velocity(body, gravity, 0.95, dt)

    def get_pos(self):
        return self.body.position.x, self.collider.y, self.body.position.y

    def set_pos(self, pos):
        self.body.position = pos[::2]
        self.body.velocity *= 0
        self.collider.y = pos[1]

    def despawn(self):
        self.app.physics.space.remove(self.body, self.collider)
        Enemy.despawn(self)

    def add_collider(self, c):
        if c.y - self.height < self.collider.y < c.y + c.height:
            if c is self.app.game_manager.player.collision.collider:
                self.app.game_manager.player.damage(40)

    def remove_collider(self, other):
        pass

    def update(self, dt):
        player_pos = self.app.game_manager.player.graphics.pos
        dx = (player_pos.x - self.body.position.x)
        dz = (player_pos.z - self.body.position.y)

        mag = ((dx ** 2) + (dz ** 2)) ** .5
        speed = self.speed / mag
        self.body.apply_impulse_at_local_point((dx * speed, dz * speed))

        Enemy.update(self, dt)

        self.color.a = 1 - (mag - 5) / 10.0

        self.health_bar.color.a = self.color.a

        self.pos.xyz = self.get_pos()


class Turret(Enemy):
    radius = 2
    height = 6

    lead_factor = .035

    range = 60

    timer = 1

    max_health = 45.0

    def __init__(self, app, pos):
        Enemy.__init__(self, app, pos, 6)
        with self.canvas:
            self.app.graphic_data.draw_mesh('models/turret',
                                            self.canvas,
                                            'metal.jpg')

            PopMatrix()

            Color(1, 1, 1, 1)

            PushMatrix()
            Translate(pos[0], pos[1] - 6, pos[2])
            Scale(3, 2, 3)

            self.app.graphic_data.draw_mesh('models/barrel',
                                            self.canvas,
                                            'download.jpg')

    def spawn_collider(self):
        self.collider = pymunk.Circle(self.app.physics.space.static_body,
                                      self.radius, self.pos.xyz[::2])
        self.collider.damage_object = self
        self.collider.y = self.pos.y
        self.collider.height = self.height
        self.collider.collision_type = physics.STATIC
        self.collider.filter = pymunk.ShapeFilter(categories=physics.STATIC_FILTER)

        self.app.physics.space.add(self.collider)

    def despawn(self):
        self.app.physics.space.remove(self.collider)
        Enemy.despawn(self)

    def update(self, dt):
        player_pos = self.app.game_manager.player.graphics.pos
        player_vel = self.app.game_manager.player.collision.body.velocity
        dx = player_pos.x - self.pos.x
        dz = player_pos.z - self.pos.z

        dist = ((dx ** 2) + (dz ** 2)) ** .5
        dx += player_vel[0] * dist * self.lead_factor
        dz += player_vel[1] * dist * self.lead_factor

        self.rot.angle = math.atan2(dx, dz) * 57.3

        dy = (player_pos.y - (self.pos.y + 2))

        self.timer -= dt * 2
        if self.timer < 0:

            mag = ((dx ** 2) + (dz ** 2)) ** .5
            if mag < self.range:
                self.timer = 1

                nx = dx / mag
                nz = dz / mag

                slope = dy / mag

                if abs(slope) < .5:
                    self.app.game_manager.add_bullet((self.pos.x + nx * 3,
                                                      self.pos.y + 4,
                                                      self.pos.z + nz * 3),
                                                     (nx, slope, nz), 30,
                                                     (1, 0, 0))

        Enemy.update(self, dt)
