from kivy.graphics import *

import util

WALK, JUMPING, DRIVING, DIE, WIN, GRAB = xrange(6)


class Character:
    state = -1
    anim_timer = 0

    def __init__(self, app):
        self.app = app

        self.colors = set()

        self.canvas = Canvas()
        with self.canvas:
            PushMatrix()

            self.pos = Translate()
            self.colors.add(Color())

            PushMatrix()
            Translate(0, 3.75, 0)
            self.head_yaw = Rotate(0, 0, 1, 0)
            self.head_pitch = Rotate(0, 1, 0, 0)
            self.app.graphic_data.draw_mesh('models/robot_head',
                                            self.canvas,
                                            'robot_texture.jpg')
            PopMatrix()

            self.colors.add(Color())

            self.rot = Rotate(0, 0, 1, 0)
            self.app.graphic_data.draw_mesh('models/robot_body',
                                            self.canvas,
                                            'robot_texture.jpg')

            PushMatrix()
            Translate(0, 3.25, 1.25)
            self.right_arm_rot = Rotate(0, 0, 0, 1)
            self.right_arm_roll = Rotate(-30, 1, 0, 0)
            self.app.graphic_data.draw_mesh('models/robot_arm',
                                            self.canvas,
                                            'robot_texture.jpg')
            PopMatrix()

            PushMatrix()
            Translate(0, 3.25, -1.25)
            self.left_arm_rot = Rotate(0, 0, 0, 1)
            self.left_arm_roll = Rotate(30, 1, 0, 0)
            self.app.graphic_data.draw_mesh('models/robot_arm',
                                            self.canvas,
                                            'robot_texture.jpg')
            PopMatrix()

            PushMatrix()
            Translate(0, 1.75, .4)
            self.right_leg_rot = Rotate(0, 0, 0, 1)
            self.app.graphic_data.draw_mesh('models/robot_leg',
                                            self.canvas,
                                            'robot_texture.jpg')
            PopMatrix()

            PushMatrix()
            Translate(0, 1.75, -.4)
            self.left_leg_rot = Rotate(0, 0, 0, 1)
            self.app.graphic_data.draw_mesh('models/robot_leg',
                                            self.canvas,
                                            'robot_texture.jpg')
            PopMatrix()

            PushMatrix()

            self.color = Color(1, 1, 1)
            Translate(-.5, 3, 0)
            Scale(.75)
            self.app.graphic_data.draw_mesh('models/jetpack',
                                            self.canvas,
                                            'robot_texture.jpg')

            Color(1, 0, 0, 1)
            Rotate(270, 0, 1, 0)
            Translate(-.8, .55, .5)
            Scale(.8, .8, 1)
            self.scale = Scale()

            self.app.graphic_data.draw_mesh('models/health_bar',
                                            self.canvas,
                                            texture=None)
            PopMatrix()
            PopMatrix()

    def set_color(self, color):
        for c in self.colors:
            c.rgb = color

    def do_animation(self, player, dt):
        speed = 10 * dt

        if player.attacking:
            arm_angle = 90 - self.app.renderer.cam_pitch.angle
            self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, 0, speed)
            self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 0, speed)
            self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, arm_angle, speed * 2)
            self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, arm_angle, speed * 2)
            # self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, 135, speed)
            # self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 60, speed)
            # self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, -40, speed * 2)
            # self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, 135, speed * 2)

        if player.state == DRIVING:
            self.right_leg_rot.angle = 90
            self.left_leg_rot.angle = 90

            if player.vehicle is not None:
                self.rot.angle = player.vehicle.rot.angle

        elif player.state == WALK:
            vel = player.get_velocity()
            self.anim_timer += dt * vel
            arm_swing = 6 * vel
            swing_time = 7

            self.right_leg_rot.angle = arm_swing * util.loop_time(self.anim_timer, swing_time)
            self.left_leg_rot.angle = -arm_swing * util.loop_time(self.anim_timer, swing_time)

            if not player.attacking:
                self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, -5, speed)
                self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 5, speed)
                self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle,
                                                         -arm_swing * util.loop_time(self.anim_timer,
                                                                                     swing_time),
                                                         speed)
                self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle,
                                                        arm_swing * util.loop_time(self.anim_timer,
                                                                                   swing_time),
                                                        speed)

        elif player.state == JUMPING:
            lean = player.input_vector[1] * 50

            self.right_leg_rot.angle = util.lerp_int(self.right_leg_rot.angle, lean, speed)
            self.left_leg_rot.angle = util.lerp_int(self.left_leg_rot.angle, lean, speed)

            if not player.attacking:
                self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, -20, speed)
                self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 20, speed)
                self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, lean, speed)
                self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, lean, speed)

        elif player.state == DIE:
            speed = dt * 10

            self.right_leg_rot.angle = util.lerp_int(self.right_leg_rot.angle, 90, speed)
            self.left_leg_rot.angle = util.lerp_int(self.left_leg_rot.angle, 90, speed)
            self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, 0, speed)
            self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, 0, speed)

            self.pos.y = player.collision.collider.y - 1.5

        elif player.state == WIN:
            speed = dt * 3

            self.right_leg_rot.angle = util.lerp_int(self.right_leg_rot.angle, -20, speed)
            self.left_leg_rot.angle = util.lerp_int(self.left_leg_rot.angle, 20, speed)
            self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, 130, speed)
            self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, 0, speed)
            self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, 0, speed)
            self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 30, speed)

        elif player.state == GRAB:
            speed = dt * 30

            self.right_leg_rot.angle = util.lerp_int(self.right_leg_rot.angle, 20, speed)
            self.left_leg_rot.angle = util.lerp_int(self.left_leg_rot.angle, 20, speed)
            self.right_arm_rot.angle = util.lerp_int(self.right_arm_rot.angle, 130, speed)
            self.left_arm_rot.angle = util.lerp_int(self.left_arm_rot.angle, 130, speed)
            self.right_arm_roll.angle = util.lerp_int(self.right_arm_roll.angle, -20, speed)
            self.left_arm_roll.angle = util.lerp_int(self.left_arm_roll.angle, 20, speed)

