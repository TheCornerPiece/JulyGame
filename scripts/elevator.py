import building, character


class Elevator(building.Building):
    data = {'mesh_name': 'models/elevator',
             'texture': 'metal.jpg',
            'colliders': [[[6.0, -3.0, 6.0, -6.0, 5.4, -6.0, 5.4, -3.0], 0.0, 11.6],
                          [[6.0, 3.0, 6.0, 6.0, 5.4, 6.0, 5.4, 3.0], 0.0, 11.6],
                          [[6.0, -6.0, 6.0, 6.0, 5.4, 6.0, 5.4, -6.0], 9.0, 2.6],
                          [[-6.0, -6.0, -6.0, -5.4, 6.0, -5.4, 6.0, -6.0], 0.0, 11.6],
                          [[-6.0, 6.0, -6.0, 5.4, 6.0, 5.4, 6.0, 6.0], 0.0, 11.6],
                          [[-6.0, -6.0, -5.4, -6.0, -5.4, 6.0, -6.0, 6.0], 0.0, 11.6],
                          [[-6.0, -6.0, -6.0, 6.0, 6.0, -6.0, 6.0, 6.0], 10.65, 0.77],
                          [[-6.0, -6.0, -6.0, 6.0, 6.0, -6.0, 6.0, 6.0], 0.0, 0.75]],
            'doors': [],
            'stairs': []}

    def __init__(self, app, pos, angle):
        building.Building.__init__(self, app, self.data, pos, angle)

        for i, c in enumerate(self.colliders):
            if i < 6:
                c.no_grab = True
            c.parent = self
        self.colliders[-1].on_stand = self.on_stand

        self.timer = 0
        self.last_direction = -5
        self.dy = 0

    def on_stand(self):
        if self.timer <= 0:
            self.last_direction *= -1
            self.dy = self.last_direction
            self.timer = 4

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

            dy = self.dy * dt
            self.pos.y += dy
            for i, c in enumerate(self.colliders):
                c.y = self.pos.y + self.data['colliders'][i][1]

            for i, d in enumerate(self.doors):
                y = self.pos.y + self.data['doors'][i][1]
                d.collider.y = y
                d.pos.y = y

            if self.timer <= 0:
                self.dy = 0
                player = self.app.game_manager.player
                if player.state == character.GRAB and player.collision.dy != 0:
                    player.collision.dy = 0
