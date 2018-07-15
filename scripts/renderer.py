from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.resources import resource_find

post_processing = '''
    #ifdef GL_ES
    precision highp float;
    #endif

    /* Outputs from the vertex shader */
    varying vec4 frag_color;
    varying vec2 tex_coord0;

    /* uniform texture samplers */
    uniform sampler2D texture0;

    void main(void)
    {
        float blur = abs((tex_coord0.x - .5) + (tex_coord0.y - .5));
        vec2 samplePos;
        samplePos.x = tex_coord0.x;
        samplePos.y = tex_coord0.y + pow(abs(tex_coord0.x - .5), 3) * (.5 - tex_coord0.y) * 2;

        if (samplePos.y > 1){
            gl_FragColor = vec4(0, 0, 0, 1);
        }
        else{
            gl_FragColor = texture2D(texture0, samplePos) * frag_color;
        }
    }
    '''


class Renderer(FloatLayout):
    min_pitch = -60
    max_pitch = 90

    shadows = False

    shadowmap_resolution = 2 ** 11

    def __init__(self, app):
        self.app = app

        self.canvas = RenderContext(use_parent_projection=True)
        # self.canvas.shader.fs = post_processing

        self.scene = InstructionGroup()

        FloatLayout.__init__(self, size_hint=(1, 1))

        with self.canvas:
            Callback(self.setup_gl)
            if self.shadows:
                self.light_fbo = Fbo(size=[self.shadowmap_resolution] * 2,
                                     compute_normal_matrix=True,
                                     with_depthbuffer=True)
                BindTexture(texture=self.light_fbo.texture, index=1)
            self.fbo = Fbo(use_parent_projection=False,
                           compute_normal_matrix=True,
                           with_depthbuffer=True)
            Callback(self.reset_gl)

            self.rect = Rectangle()

        if self.shadows:
            with self.light_fbo:
                ClearColor(1, 0, 1, 1)
                ClearBuffers(clear_depth=True)

                PushMatrix()

                self.light_pitch = Rotate(90, 1, 0, 0)
                self.light_yaw = Rotate(0, 0, 1, 0)
                self.light_pos = Translate(4, -50, 0)

                Callback(self.set_light_viewmat)

                self.light_fbo.add(self.scene)

                PopMatrix()

            self.light_fbo.shader.source = resource_find('shaders/light.glsl')
            self.light_fbo['projection_mat'].perspective(90.0, 1.0, .1, 100)

        with self.fbo:
            PushMatrix()
            ClearColor(.7, .7, 1, 1)
            ClearBuffers(clear_depth=True)
            self.cam_offset = Translate(0, 0, 0)
            self.cam_pitch = Rotate(0, 1, 0, 0)
            self.cam_yaw = Rotate(0, 0, 1, 0)
            self.cam_pos = Translate()

            Callback(self.set_fbo_viewmat)

            self.fbo.add(self.scene)

            PopMatrix()

        if self.shadows:
            self.fbo.shader.source = resource_find('shaders/shadow.glsl')
            self.fbo['lightmap'] = 1
        else:
            self.fbo.shader.source = resource_find('shaders/clip_shader.glsl')

        self.target_pos = (0, 0, 0)

        self.particle_yaw = Rotate(0, 0, 1, 0)
        self.particle_pitch = Rotate(0, 1, 0, 0)

    # def on_touch_move(self, touch):
    #     self.light_pitch.angle = min(85, max(-65, self.light_pitch.angle - touch.dy))
    #     self.light_yaw.angle += touch.dx

    def set_light_viewmat(self, *args):
        self.light_fbo['inv_view_mat'] = self.light_fbo['modelview_mat'].inverse()
        self.fbo['light_view_mat'] = self.light_fbo['modelview_mat']
        self.fbo['light_viewprojection_mat'] = self.light_fbo['projection_mat'].multiply(
            self.light_fbo['modelview_mat'])

    def set_fbo_viewmat(self, *args):
        self.fbo['inv_view_mat'] = self.fbo['modelview_mat'].inverse()

    def on_size(self, *args):
        self.fbo.size = self.size
        self.rect.size = self.size
        self.rect.texture = self.fbo.texture
        # self.rect.texture = self.light_fbo.texture
        self.set_matrix()

    def on_pos(self, *args):
        self.rect.pos = self.pos

    def rotate_camera(self, dt, yaw=0, pitch=0):
        self.cam_yaw.angle += yaw * dt
        self.cam_pitch.angle += pitch * dt
        if self.cam_pitch.angle < self.min_pitch:
            self.cam_pitch.angle = self.min_pitch
        elif self.cam_pitch.angle > self.max_pitch:
            self.cam_pitch.angle = self.max_pitch

    def set_matrix(self):
        self.fbo['projection_mat'].perspective(90, self.width / float(self.height),
                                               3.5, 1000)

    def update(self, dt):
        self.particle_yaw.angle = -self.cam_yaw.angle
        self.particle_pitch.angle = -self.cam_pitch.angle

        if self.shadows:
            self.light_fbo.ask_update()
        self.rotate_camera(dt, *self.app.input_manager.camera_axis)

        diff = [j - i for i, j in zip(self.cam_pos.xyz, self.target_pos)]

        mag_sqrd = sum([i ** 2 for i in diff])

        speed = mag_sqrd * 5.0 * dt
        if mag_sqrd > speed ** 2:
            mag = mag_sqrd ** .5
            self.cam_pos.xyz = [i + (j / mag) * speed for i, j in zip(self.cam_pos.xyz, diff)]
        else:
            self.cam_pos.xyz = self.target_pos

        if self.shadows:
            self.light_pos.x = self.cam_pos.x
            self.light_pos.y = self.cam_pos.y - 50
            self.light_pos.z = self.cam_pos.z

    def set_cam_pos(self, pos):
        self.target_pos = pos

    def setup_gl(self, cb):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def reset_gl(self, cb):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
