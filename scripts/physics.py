import pymunk

DEFAULT, DYNAMIC, STATIC, BULLET = xrange(4)

# filters
DEFUALT, BULLET_FILTER, DOOR_FILTER, STATIC_FILTER = [2 ** i for i in xrange(4)]


class PhysicsManager:
    def __init__(self, app):
        self.app = app
        self.space = pymunk.Space()
        self.space.collision_slop = 0

        handler = self.space.add_collision_handler(DYNAMIC, STATIC)
        # handler.begin = self.dynamic_static_begin
        handler.pre_solve = self.dynamic_static_presolve
        handler.separate = self.dynamic_static_leave

        handler = self.space.add_wildcard_collision_handler(BULLET)
        handler.begin = self.bullet_begin

        handler = self.space.add_collision_handler(DYNAMIC, DYNAMIC)
        handler.begin = self.dynamic_begin
        handler.pre_solve = self.dynamic_presolve
        handler.separate = self.dynamic_leave

    def dynamic_begin(self, arbiter, space, data):
        a, b = arbiter.shapes
        a.parent.add_collider(b)
        b.parent.add_collider(a)
        return True

    def dynamic_presolve(self, arbiter, space, data):
        a, b = arbiter.shapes
        b_height = b.height - b.parent.step_height
        a_height = a.height - a.parent.step_height

        if a.y - b_height < b.y < a.y + a_height:
            return True
        else:
            return False

    def dynamic_leave(self, arbiter, space, data):
        a, b = arbiter.shapes
        a.parent.remove_collider(b)
        b.parent.remove_collider(a)

    def bullet_begin(self, arbiter, space, data):
        b_col, other = arbiter.shapes

        if other.y < b_col.parent.pos.y < other.y + other.height:
            self.app.game_manager.remove_object(b_col.parent)
            if hasattr(other, 'damage_object'):
                other.damage_object.damage(15)
            return True
        else:
            return False

    def dynamic_static_presolve(self, arbiter, space, data):
        dynamic, col = arbiter.shapes

        min_y = col.y - dynamic.height
        push_y = min_y + 1.0
        max_y = col.y + (col.height - dynamic.parent.step_height)

        point_set = arbiter.contact_point_set
        dist = abs(point_set.points[0].distance)

        if min_y < dynamic.y < max_y:
            if dynamic.y < push_y and dist > 0.3:
                dynamic.y = min_y
                return False
            elif col.body == space.static_body and dynamic == self.app.game_manager.player.collision.collider:
                self.app.game_manager.player.hit_collider(col, arbiter.contact_point_set)
            return True
        elif dist > 0.3:
            dynamic.parent.add_collider(col)
            return False
        else:
            dynamic.parent.remove_collider(col)

        return False

    def dynamic_static_leave(self, arbiter, space, data):
        dynamic, other = arbiter.shapes

        dynamic.parent.remove_collider(other)
        return True

    def update(self, dt):
        self.space.step(dt)
