import pymunk

import model, bullet, physics, particle, bullet_particle


class ResourceManager:
    def __init__(self, app):
        self.app = app

        # GRAPHICS
        self.model_cache = set()

        self.bullet_cache = set()

        # PHYSICS
        self.circle_cache = set()
        self.body_cache = set()

        self.bullet_particle_cache = set()
        self.particle_cache = set()

        self.count = 0

    def debug(self):
        print '{} / {}'.format(self.count - len(self.model_cache), self.count)

    def get_particle(self, pos, vel, particle_type=0):
        if particle_type == 0:
            if self.particle_cache:
                p = self.particle_cache.pop()
            else:
                p = particle.Particle(self.app)
        else:
            if self.bullet_particle_cache:
                p = self.bullet_particle_cache.pop()
            else:
                p = bullet_particle.BulletParticle(self.app)
        p.spawn(pos, vel)
        return p

    def cache_particle(self, p, particle_type=0):
        if particle_type == 0:
            self.particle_cache.add(p)
        else:
            self.bullet_particle_cache.add(p)

    def get_bullet(self, pos, vel, speed, color):
        if self.bullet_cache:
            b = self.bullet_cache.pop()
        else:
            b = bullet.Bullet(self.app)
        b.spawn(pos, vel, speed, color)
        return b

    def cache_bullet(self, b):
        self.bullet_cache.add(b)

    def get_model(self, filename, texture=None, pos=(0, 0, 0), angle=0):
        if self.model_cache:
            m = self.model_cache.pop()
        else:
            self.count += 1
            m = model.Model(self.app)

        m.set_mesh(filename, texture)
        m.pos.xyz = pos
        m.rot.angle = angle
        m.add_collider()
        return m

    def get_circle(self, parent=None, offset=(0, 0, 0), radius=.5, height=1, collision_type=0):
        if self.circle_cache:
            circle = self.circle_cache.pop()
            circle.unsafe_set_radius(radius)
            circle.unsafe_set_offset(offset[::2])
        else:
            circle = pymunk.Circle(self.app.physics.space.static_body,
                                   radius, offset[::2])

        circle.collision_type = collision_type
        circle.filter = pymunk.ShapeFilter(categories=physics.STATIC_FILTER)
        circle.height = height
        circle.y = offset[1]
        if parent is not None:
            circle.parent = parent

        self.app.physics.space.add(circle)
        return circle

    def get_body(self, pos=(0, 0), angle=0):
        if self.body_cache:
            body = self.body_cache.pop()
            body.position = pos
            body.angle = angle
            body.velocity *= 0
        else:
            body = pymunk.Body()

    def cache_model(self, m):
        self.model_cache.add(m)
        m.remove_collider()
        self.app.renderer.remove_object(m)

    def cache_circle(self, circle):
        self.circle_cache.add(circle)
        self.app.physics.space.remove(circle)
