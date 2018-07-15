import main

from kivy.core.window import Window
from kivy.uix.widget import Widget

AXIS_MAX = 32767.0

# BUTTONS
A = 0
B = 1
X = 2
Y = 3
START = 7

# AXIS
LX = 0
LY = 1
RX = 3
RY = 4
RT = 5
LT = 2


class InputManager(Widget):
    dead_zone = .35

    x_sensitivity = .9
    y_sensitivity = -.7

    joy_x_sensitivity = 3 * 60
    joy_y_sensitivity = 2 * 60

    invert_y = 1

    def __init__(self, app):
        self.app = app
        Widget.__init__(self)

        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        self.axis = [0, 0]
        self.camera_axis = [0, 0]

        self.last_pressed = None

    def on_touch_down(self, touch):
        return not self.app.paused

    def on_touch_move(self, touch):
        if self.app.state == main.GAME:
            self.app.renderer.rotate_camera(touch.dx * self.x_sensitivity,
                                            touch.dy * self.y_sensitivity)
        return False

    def on_joy_axis(self, window, joystick, axis, value):
        value /= AXIS_MAX
        if abs(value) < self.dead_zone:
            value = 0

        if axis == LX:
            self.axis[0] = value
            self.app.game_manager.player.set_axis(self.axis)
        elif axis == LY:
            self.axis[1] = value
            self.app.game_manager.player.set_axis(self.axis)
        elif axis == RX:
            self.camera_axis[0] = value * abs(value) * self.joy_x_sensitivity
        elif axis == RY:
            self.camera_axis[1] = value * self.joy_y_sensitivity * self.invert_y
        elif axis == RT:
            if value > .5:
                self.app.game_manager.player.right_trigger_down()
            else:
                self.app.game_manager.player.right_trigger_up()
        elif axis == LT:
            if value > .5:
                self.app.game_manager.player.left_trigger_down()
            else:
                self.app.game_manager.player.left_trigger_up()
        # print axis, value

    def on_joy_button_down(self, window, joystick, button):
        if button == START:
            self.app.on_esc()
        elif button == A:
            self.app.game_manager.player.do_jump()
        # elif button == B:
        #     self.app.game_manager.player.do_dab()
        elif button == Y:
            self.app.game_manager.player.drive()
        # elif button == X:
        #     self.app.click_button(3)

    def on_joy_button_up(self, window, joystick, button):
        if button == A:
            self.app.game_manager.player.stop_jump()
        elif button == B:
            self.app.set_state(main.MENU)
    #     elif button == Y:
    #         self.app.release_button(2)
    #     elif button == X:
    #         self.app.release_button(3)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def add_axis(self, axis, value):
        self.axis[axis] = cmp(self.axis[axis] + value, 0)
        self.app.game_manager.player.set_axis(self.axis)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key_id, key_text = keycode

        if key_id != self.last_pressed:
            self.last_pressed = key_id

            if key_text == 'escape':
                self.app.on_esc()
            elif key_text == 'w':
                self.add_axis(1, -1)
            elif key_text == 's':
                self.add_axis(1, 1)
            elif key_text == 'd':
                self.add_axis(0, 1)
            elif key_text == 'a':
                self.add_axis(0, -1)
            elif key_text == 'spacebar':
                self.app.game_manager.player.do_jump()
            elif key_text == 'shift':
                self.app.game_manager.player.right_trigger_down()
            else:
                print key_text

        return True

    def _on_keyboard_up(self, keyboard, keycode):
        key_id, key_text = keycode

        if key_text == 'w':
            self.add_axis(1, 1)
        elif key_text == 's':
            self.add_axis(1, -1)
        elif key_text == 'd':
            self.add_axis(0, -1)
        elif key_text == 'a':
            self.add_axis(0, 1)
        elif key_text == 'spacebar':
            self.app.game_manager.player.stop_jump()
        elif key_text == 'shift':
            self.app.game_manager.player.right_trigger_up()

        if key_id == self.last_pressed:
            self.last_pressed = None

        return True
