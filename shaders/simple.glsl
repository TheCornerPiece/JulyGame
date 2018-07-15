---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc;
attribute float v_tex;

uniform vec4 color;
uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 frag_color;
varying vec2 uv_vec;
varying vec4 normal_vec;
varying vec4 vertex_pos;

void main (void) {
    vec4 viewPos = modelview_mat * vec4(v_pos,1.0);
    gl_Position = projection_mat * viewPos;
    frag_color = color;
    uv_vec = v_tc;
    vertex_pos = viewPos;
    normal_vec = modelview_mat * vec4(v_normal, 0.0);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

uniform mat4 normal_mat;
uniform sampler2D tex_0;

varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec2 uv_vec;
varying vec4 frag_color;

const float v = .4;

void main (void){
    float theta = dot(normal_vec, vec4(0, 0, 1, 1)) * v + (1-v);
    vec4 color = texture2D(tex_0, uv_vec);
    gl_FragColor = color * vec4(theta, theta, theta, 1.0) * frag_color;
}