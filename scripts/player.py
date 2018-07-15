import math
import pymunk

import character, dynamic_object, util


class Player:
    speed = .9
    turn_speed = 5
    base_jump_force = 10
    jump_force = 20
    jump_time = .4

    radius = 1
    height = 4.5

    attack_timer = 0
    state_timer = 0

    damage_speed = 40
    fall_damage = 2
    arm_index = 1

    slow_motion_time = 0
    powerup_time = 0

    net_pos = [0, 0, 0]
    net_angle = 0

    target_angle = 0
    attacking = False
    vehicle = None
    input_vector = [0, 0]

    max_health = 100.0
    damage_timer = 0
    health = max_health

    def __init__(self, app):
        self.app = app

        self.collision = dynamic_object.DynamicObject(self.app, self)
        self.collision.spawn_collider(self.app, pymunk.Circle(None, self.radius),
                                      0, self.height)

        self.collision.collider.damage_object = self

        self.graphics = character.Character(self.app)

        self.collision.spawn((0, 0, 0))

        self.set_state(character.JUMPING)

    def hit_collider(self, col, point_set):
        if self.state == character.JUMPING:
            top = col.y + col.height
            min_y = top - self.height
            max_y = top - self.height * .5
            y_pos = self.collision.collider.y

            if min_y < y_pos < max_y:
                if not hasattr(col, 'no_grab'):
                    self.graphics.rot.angle = math.atan2(-point_set.normal.y, point_set.normal.x) * 57.3
                    self.graphics.pos.y = top - (self.height - .5)
                    self.collision.collider.y = self.graphics.pos.y
                    self.collision.body.velocity *= 0
                    self.set_state(character.GRAB)

                    if util.is_elevator(col):
                        self.collision.dy = col.parent.dy
                    else:
                        self.collision.dy = 0

    def get_velocity(self):
        return self.collision.get_velocity()

    def spawn(self, pos):
        self.graphics.pos.xyz = pos
        self.stop_powerup()
        self.health = self.max_health
        self.app.gui_manager.set_health(self.health)
        self.graphics.scale.x = 1

        if self.state == character.DRIVING:
            self.vehicle = None
            self.collision.spawn(pos)
        else:
            self.collision.set_pos(pos)
        self.set_state(character.JUMPING)
        self.collision.dy = 0
        self.state_timer = 0

    def set_standing(self, c, shape=True):
        if shape and hasattr(c, 'on_stand'):
            c.on_stand()
        if self.collision.dy > 0:
            return True
        else:
            if self.state != character.WIN:
                over_speed = self.collision.dy + self.damage_speed
                if over_speed < 0:
                    self.damage(-over_speed * self.fall_damage)
                if self.health > 0:
                    self.set_state(character.WALK)

    def removed_standing(self):
        if self.state == character.WALK:
            self.set_state(character.JUMPING)
            self.state_timer = 0

    def drive(self):
        if self.state == character.DRIVING:
            self.collision.spawn(self.graphics.pos.xyz)
            self.collision.body.velocity = self.vehicle.collision.body.velocity
            self.collision.dy = self.vehicle.collision.dy

            self.vehicle.accel = 0
            self.vehicle.turn = 0
            self.vehicle.turn_off()

            self.set_state(character.JUMPING)
        else:
            for vehicle in self.app.game_manager.vehicles:
                if util.sqr_distance_between(self.graphics.pos.xyz, vehicle.pos.xyz) < 50:
                    self.vehicle = vehicle
                    self.set_state(character.DRIVING)
                    break

    def do_jump(self):
        if self.state == character.GRAB:
            rads = self.graphics.rot.angle / 57.3

            cos = math.cos(rads)
            sin = math.sin(rads)

            self.collision.body.apply_impulse_at_local_point((-cos * 10, sin * 10))
            self.collision.dy = self.base_jump_force
            self.set_state(character.JUMPING)
        elif (self.state == character.JUMPING and self.powerup_time > 0) or self.state == character.WALK:
            self.collision.dy = self.base_jump_force
            self.set_state(character.JUMPING)

    def stop_jump(self):
        if self.state == character.JUMPING:
            self.state_timer = 0

    def start_attack(self):
        if self.state in (character.WALK, character.JUMPING):
            self.attacking = True
            self.attack_timer = 1

    def stop_attack(self):
        self.attacking = False

    def start_slow_motion(self):
        self.slow_motion_time = 1
        self.app.time_scale = .5

    def stop_slow_motion(self):
        self.slow_motion_time = 0
        self.app.time_scale = 1

    def set_state(self, state):
        self.app.network_manager.send_message('s|{};'.format(state))
        if state == character.DRIVING:
            self.attacking = False
            self.app.renderer.cam_offset.z = -15
            self.state = state
            self.collision.despawn()
        else:
            self.app.renderer.cam_offset.z = -6

            if state == character.WALK:
                self.collision.dy = 0

            elif state == character.JUMPING:
                self.state_timer = self.jump_time
                self.collision.standing = None

        self.state = state

    def start_powerup(self):
        self.powerup_time = 1
        self.graphics.color.rgb = (0, 0, 1)
        self.app.gui_manager.set_powerup(self.powerup_time)

    def stop_powerup(self):
        self.powerup_time = 0
        self.app.gui_manager.set_powerup(0)
        self.graphics.color.rgb = 1, 1, 1

    def set_axis(self, axis):
        self.input_vector = axis

    def despawn(self):
        pass

    def get_health(self):
        self.health = 100
        self.app.gui_manager.set_health(self.health)
        self.graphics.scale.x = self.health / self.max_health

    def damage(self, amt):
        if self.state != character.WIN:
            if self.state == character.GRAB:
                self.set_state(character.JUMPING)
            self.damage_timer = 1
            self.health -= amt
            if self.health <= 0:
                self.health = 0
                self.set_state(character.DIE)
                self.app.level_manager.set_level(self.app.level_manager.level_id)
            self.app.gui_manager.set_health(self.health)
            self.graphics.scale.x = self.health / self.max_health

    def update(self, dt):
        if self.state in (character.DIE, character.WIN):
            self.collision.dy -= self.collision.gravity * dt
            if not self.collision.standing:
                self.collision.move_y(dt)
            self.collision.update(dt)

            self.graphics.pos.xyz = self.collision.get_pos()

            self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                           -(self.graphics.pos.y + 3),
                                           -self.graphics.pos.z))

        else:
            if self.state == character.DRIVING:
                self.vehicle.move(self.input_vector, dt)
                self.app.renderer.cam_yaw.angle = 90 - self.graphics.rot.angle

                self.graphics.pos.x = self.vehicle.pos.x
                self.graphics.pos.y = self.vehicle.pos.y + self.vehicle.seat_offset
                self.graphics.pos.z = self.vehicle.pos.z

                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + 7 + self.vehicle.seat_offset),
                                               -self.graphics.pos.z))
            elif self.state == character.GRAB:
                if self.collision.move_y(dt):
                    self.set_state(character.WALK)

                self.graphics.pos.xyz = self.collision.get_pos()
                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + 7),
                                               -self.graphics.pos.z))
            else:
                self.move(self.input_vector, self.speed, dt)

                if self.state == character.JUMPING:
                    if self.state_timer <= 0:
                        self.collision.dy -= self.collision.gravity * dt
                        if self.collision.move_y(dt) and self.state != character.DIE:
                            self.set_state(character.WALK)
                    else:
                        self.state_timer -= dt
                        if self.powerup_time > 0:
                            self.collision.dy += self.jump_force * dt * 1.2
                            self.powerup_time -= dt
                            if self.powerup_time < 0:
                                self.stop_powerup()
                            else:
                                self.app.gui_manager.set_powerup(self.powerup_time)

                            rads = (self.graphics.rot.angle - 90) / 57.3
                            x = self.graphics.pos.x + math.sin(rads) * 2 + util.random_value(.3)
                            z = self.graphics.pos.z + math.cos(rads) * 2 + util.random_value(.3)

                            pos = (x, self.graphics.pos.y + 2, z)
                            vel = (util.random_value(4), -4, util.random_value(4))

                            test_particle = self.app.resource_manager.get_particle(pos, vel, 0)
                            self.app.renderer.scene.add(test_particle.canvas)
                            self.app.game_manager.game_objects.add(test_particle)
                        else:
                            self.collision.dy += self.jump_force * dt

                        self.collision.move_y(dt)

                if self.attacking:
                    cam_height = 8
                else:
                    cam_height = 6
                self.app.renderer.set_cam_pos((-self.graphics.pos.x,
                                               -(self.graphics.pos.y + cam_height),
                                               -self.graphics.pos.z))

                self.collision.update(dt)

                self.graphics.pos.xyz = self.collision.get_pos()

                if self.damage_timer > 0:
                    self.damage_timer -= dt * 2

                    if self.damage_timer > 0:
                        i = 1 - self.damage_timer

                        self.graphics.set_color((1, i, i))
                    else:
                        self.graphics.set_color((1, 1, 1))

            self.graphics.head_pitch.angle = -self.app.renderer.cam_pitch.angle
            self.graphics.head_yaw.angle = -self.app.renderer.cam_yaw.angle

            diff = sum([abs(i - j) for i, j in zip(self.net_pos, self.graphics.pos.xyz)])
            if diff > .5:
                self.net_pos = self.graphics.pos.xyz
                pos = [round(i, 2) for i in self.graphics.pos.xyz]
                self.app.network_manager.send_message('p|{}|{}|{}|{};'.format(pos[0], pos[1], pos[2],
                                                                              int(self.get_velocity())))

            if abs(self.graphics.rot.angle - self.net_angle) > 10:
                self.net_angle = int(self.graphics.rot.angle)
                self.app.network_manager.send_message('a|{};'.format(self.net_angle))

            if self.attacking:
                self.attack_timer -= dt * 5
                if self.attack_timer < 0:
                    self.attack_timer = 1
                    self.arm_index *= -1
                    x, y, z, dx, dy, dz = self.get_hand_pos(self.arm_index)
                    self.app.game_manager.add_bullet((x, y, z), (dx, dy, dz), 20, (0, 0, 1))

        if self.slow_motion_time > 0:
            self.slow_motion_time -= dt * .1
            if self.slow_motion_time < 0:
                self.stop_slow_motion()

        self.graphics.do_animation(self, dt)

    def move(self, direction, speed, dt):
        if any(direction):
            ix, iy = direction

            rads = self.app.renderer.cam_yaw.angle / 57.3
            cos = math.cos(rads)
            sin = math.sin(rads)

            dx = cos * ix + -sin * iy
            dy = sin * ix + cos * iy

            mag_sqrd = dx ** 2 + dy ** 2

            if mag_sqrd > 1:
                s = speed / (mag_sqrd ** .5)
            else:
                s = speed
            self.collision.body.apply_impulse_at_local_point((dx * s, dy * s))

        if any(self.collision.body.velocity):
            target_angle = 90 - self.app.renderer.cam_yaw.angle
            da = util.angle_diff(self.graphics.rot.angle, target_angle)
            turn_speed = self.turn_speed * dt
            if abs(da) > turn_speed:
                self.graphics.rot.angle += da * turn_speed
            else:
                self.graphics.rot.angle = target_angle

    def get_hand_pos(self, index):
        rads = self.graphics.rot.angle / 57.3
        sin = math.cos(rads)
        cos = math.sin(rads)

        arm_rads = self.graphics.right_arm_rot.angle / 57.3
        arm_length = -1.5

        local_x = 1.2 * index
        local_z = math.sin(arm_rads) * arm_length
        local_y = math.cos(arm_rads) * arm_length

        x = self.graphics.pos.x + (cos * local_x + -sin * local_z)
        y = self.graphics.pos.y + local_y + 3.5
        z = self.graphics.pos.z + (sin * local_x + cos * local_z)

        return x, y, z, -sin * local_z, local_y, cos * local_z

    def right_trigger_down(self):
        if self.state == character.DRIVING:
            self.vehicle.right_trigger_down()
        else:
            self.start_attack()

    def right_trigger_up(self):
        if self.state == character.DRIVING:
            self.vehicle.right_trigger_up()
        else:
            self.stop_attack()

    def left_trigger_down(self):
        if self.state == character.DRIVING:
            self.vehicle.left_trigger_down()

    def left_trigger_up(self):
        if self.state == character.DRIVING:
            self.vehicle.left_trigger_up()
