import os

from kivy.uix.image import Image
from kivy.graphics import *

from objloader import ObjFile


class GraphicData:
    textures = {}
    meshes = {}

    def get_texture(self, filename):
        if filename in self.textures:
            return self.textures[filename]
        else:
            path = 'textures/{}'.format(filename)
            if os.path.exists(path):
                tex = Image(source=path).texture
                tex.wrap = 'repeat'
                self.textures[filename] = tex
                return tex
            else:
                print '{} does not exist'.format(path)

    @staticmethod
    def get_scene(filename):
        path = '{}.obj'.format(filename)
        if os.path.exists(path):
            return ObjFile(path)
        else:
            print '{} does not exist'.format(path)

    def draw_mesh(self, name, canvas=None, texture=None):
        if name in self.meshes:
            if canvas:
                for m in self.meshes[name]:
                    canvas.add(m)
        else:
            scene = self.get_scene(name)
            meshes = set()
            for obj in scene.objects.itervalues():
                m = Mesh(vertices=obj.vertices,
                         indices=obj.indices,
                         fmt=obj.vertex_format,
                         mode='triangles')
                if texture:
                    m.texture = self.get_texture(texture)
                meshes.add(m)
            self.meshes[name] = meshes

        return self.meshes[name]
