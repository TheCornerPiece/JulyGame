import player, goal, net_player, enemy, character, util, main

NORMAL, SURVIVAL = xrange(2)


class GameManager:
    enemy_count = -1
    state = -1

    def __init__(self, app):
        self.app = app

        self.player = player.Player(self.app)
        self.app.renderer.scene.add(self.player.graphics.canvas)

        self.terrain = None

        self.goal = goal.Goal(self.app)
        self.app.renderer.scene.add(self.goal.canvas)

        self.game_objects = set()
        self.vehicles = set()
        self.enemies = set()

        self.net_players = {}

    def clear_level(self):
        self.app.time_scale = 1
        for o in self.game_objects:
            o.despawn()
        for e in self.enemies:
            e.despawn()
        if self.terrain:
            self.app.renderer.scene.remove(self.terrain.canvas)
        self.vehicles.clear()
        self.game_objects.clear()
        self.enemies.clear()

    def spawn_net_player(self, client_id):
        p = net_player.NetPlayer(self.app, client_id)
        self.net_players[client_id] = p
        self.app.renderer.scene.add(p.graphics.canvas)

    def remove_net_player(self, client_id):
        if client_id in self.net_players:
            p = self.net_players[client_id]
            p.despawn()
            del self.net_players[client_id]

    def set_net_player_pos(self, client_id, pos):
        self.net_players[client_id].set_pos(pos)

    def set_net_player_angle(self, client_id, angle):
        self.net_players[client_id].set_angle(angle)

    def set_net_player_state(self, client_id, state):
        if state == character.WIN and self.player.state != character.WIN:
            if self.player.state == character.DRIVING:
                self.player.drive()
            self.player.set_state(character.WIN)
            self.goal.set_state(goal.COLLECTED)
        self.net_players[client_id].set_state(state)

    def add_bullet(self, pos, vel, speed, color):
        b = self.app.resource_manager.get_bullet(pos, vel, speed, color)
        self.game_objects.add(b)

    def remove_object(self, o):
        if o in self.game_objects:
            o.despawn()
            self.game_objects.remove(o)

    def set_state(self, state):
        if state == SURVIVAL:
            self.enemy_count = 0
            for e in self.enemies:
                if not isinstance(e, enemy.BowlSpawner):
                    self.enemy_count += 1
        self.state = state

    def killed_enemy(self):
        if self.state == SURVIVAL:
            self.enemy_count -= 1
            if self.enemy_count <= 0:
                self.player.set_state(character.WIN)
                self.app.level_manager.set_level()

    def update(self, dt):
        for o in self.game_objects.copy():
            o.update(dt)
        for p in self.net_players.itervalues():
            p.update(dt)

        if self.state == NORMAL:
            self.goal.update(dt)
        elif self.state == SURVIVAL:
            min_d = -1
            for e in self.enemies:
                d_sqrd = util.sqr_distance_between(self.player.graphics.pos.xyz, e.pos.xyz)
                if min_d == -1 or d_sqrd < min_d:
                    min_d = d_sqrd
            self.app.gui_manager.set_goal_distance(min_d)

        self.player.update(dt)
