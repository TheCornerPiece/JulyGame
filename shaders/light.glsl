---VERTEX SHADER-------------------------------------------------------
#version 330

#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc0;

uniform mat4 inv_view_mat;
uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 vertex_pos;
varying vec4 vertex_norm;

void main (void) {
    vec4 pos = modelview_mat * vec4(v_pos, 1.0);
    gl_Position = projection_mat * pos;
//    vertex_pos = pos;
    vertex_pos = gl_Position;
    vertex_norm = modelview_mat * vec4(v_normal, 0);
}


---FRAGMENT SHADER-----------------------------------------------------
#version 330

#ifdef GL_ES
    precision highp float;
#endif

uniform mat4 normal_mat;

varying vec4 vertex_pos;
varying vec4 vertex_norm;

const float v = .3;

void main (void){
    float depth = vertex_pos.z * .01;
    float normal_z = vertex_norm.z * .5 + .5;
//    float darkness = step(length(vertex_pos.xy) / vertex_pos.z, .9);
    float darkness = 1.0;
    gl_FragColor = vec4(depth, normal_z, darkness, 1.0);
}