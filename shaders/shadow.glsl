---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3 v_pos;
attribute vec3 v_normal;
attribute vec2 v_tc;
attribute float v_tex;

uniform vec4 color;
uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 inv_view_mat;
uniform mat4 light_view_mat;
uniform mat4 light_viewprojection_mat;

varying vec4 frag_color;
varying vec2 uv_vec;
varying vec4 normal_vec;
varying vec4 world_pos;
varying vec4 light_norm;
varying vec4 light_screen_pos;

void main (void) {
    mat4 model_mat = inv_view_mat * modelview_mat;
    vec4 pos = modelview_mat * vec4(v_pos,1.0);

    gl_Position = projection_mat * pos;
    frag_color = color;
    uv_vec = v_tc;
    world_pos = inv_view_mat * pos;
    light_norm = light_view_mat * model_mat * vec4(v_normal, 0.0);

    light_screen_pos = light_viewprojection_mat * world_pos;
}


---FRAGMENT SHADER-----------------------------------------------------

#ifdef GL_ES
    precision highp float;
#endif

uniform mat4 normal_mat;
uniform sampler2D tex_0;
uniform sampler2D lightmap;

varying vec4 normal_vec;
varying vec2 uv_vec;
varying vec4 frag_color;

varying vec4 world_pos;
varying vec4 light_norm;
varying vec4 light_screen_pos;

const float v = .3;
const int DEPTH = 0;
const int NORM_Z = 1;
const int FACTOR = 2;

void main (void){
    float theta = 0.7;
    float away = pow(dot(light_norm.xyz, vec3(0, 0, 1)) * .3 + .7, 2);

    if (light_screen_pos.z > 0){
        float sx = (light_screen_pos.x / light_screen_pos.z) * .5 + .5;
        float sy = (light_screen_pos.y / light_screen_pos.z) * .5 + .5;

        if (0 < sx && sx < 1 && 0 < sy && sy < 1){
            vec4 light_data = texture2D(lightmap, vec2(sx, sy));
            if (light_data[FACTOR] > 0){
                float depth = light_data[DEPTH];
                float norm_error = .005 * (1 - abs((light_norm.z * .5 + .5) - light_data[NORM_Z]));
                if ((light_screen_pos.z * .01) - norm_error < depth){
                    theta = min(1.0, theta + (1.0 - depth)) * away;
                }
            }
        }
    }

    vec4 color = texture2D(tex_0, uv_vec) * frag_color;

    gl_FragColor = color * vec4(theta, theta, theta, 1.0);
}