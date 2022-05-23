import copy
from tkinter import *
from dataclasses import dataclass
import math
from os.path import exists


@dataclass
class Vector3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Triangle:
    points: [Vector3D, Vector3D, Vector3D]
    rgb: () = (0, 0, 0)


@dataclass
class Mesh:
    triangles: []


@dataclass
class Object:
    def __init__(self, loc=None, rot=None, scale=None, color=None, mesh=None):
        if loc is None:
            loc = Vector3D(0.0, 0.0, 0.0)
        self.loc = loc
        if rot is None:
            rot = Vector3D(0.0, 0.0, 0.0)
        self.rot = rot
        if scale is None:
            scale = Vector3D(1.0, 1.0, 1.0)
        self.scale = scale
        if color is None:
            color = (200, 200, 200)
        self.color = color
        if mesh is False:
            mesh = None
        self.mesh = mesh


class Shapes:
    cube = Mesh([
        Triangle([Vector3D(0.0, 0.0, 0.0),   Vector3D(0.0, 1.0, 0.0),   Vector3D(1.0, 1.0, 0.0)]),
        Triangle([Vector3D(0.0, 0.0, 0.0),   Vector3D(1.0, 1.0, 0.0),   Vector3D(1.0, 0.0, 0.0)]),
        Triangle([Vector3D(1.0, 0.0, 0.0),   Vector3D(1.0, 1.0, 0.0),   Vector3D(1.0, 1.0, 1.0)]),
        Triangle([Vector3D(1.0, 0.0, 0.0),   Vector3D(1.0, 1.0, 1.0),   Vector3D(1.0, 0.0, 1.0)]),
        Triangle([Vector3D(1.0, 0.0, 1.0),   Vector3D(1.0, 1.0, 1.0),   Vector3D(0.0, 1.0, 1.0)]),
        Triangle([Vector3D(1.0, 0.0, 1.0),   Vector3D(0.0, 1.0, 1.0),   Vector3D(0.0, 0.0, 1.0)]),
        Triangle([Vector3D(0.0, 0.0, 1.0),   Vector3D(0.0, 1.0, 1.0),   Vector3D(0.0, 1.0, 0.0)]),
        Triangle([Vector3D(0.0, 0.0, 1.0),   Vector3D(0.0, 1.0, 0.0),   Vector3D(0.0, 0.0, 0.0)]),
        Triangle([Vector3D(0.0, 1.0, 0.0),   Vector3D(0.0, 1.0, 1.0),   Vector3D(1.0, 1.0, 1.0)]),
        Triangle([Vector3D(0.0, 1.0, 0.0),   Vector3D(1.0, 1.0, 1.0),   Vector3D(1.0, 1.0, 0.0)]),
        Triangle([Vector3D(1.0, 0.0, 1.0),   Vector3D(0.0, 0.0, 1.0),   Vector3D(0.0, 0.0, 0.0)]),
        Triangle([Vector3D(1.0, 0.0, 1.0),   Vector3D(0.0, 0.0, 0.0),   Vector3D(1.0, 0.0, 0.0)]),
    ])

    rectangular_pyramid = Mesh([
        Triangle([Vector3D(0.0, 0.0, 0.0),   Vector3D(0.5, 1.0, 0.5),   Vector3D(1.0, 0.0, 0.0)]),
        Triangle([Vector3D(1.0, 0.0, 0.0),   Vector3D(0.5, 1.0, 0.5),   Vector3D(1.0, 0.0, 1.0)]),
        Triangle([Vector3D(1.0, 0.0, 1.0),   Vector3D(0.5, 1.0, 0.5),   Vector3D(0.0, 0.0, 1.0)]),
        Triangle([Vector3D(0.0, 0.0, 1.0),   Vector3D(0.5, 1.0, 0.5),   Vector3D(0.0, 0.0, 0.0)]),
        Triangle([Vector3D(0.0, 0.0, 1.0),   Vector3D(0.0, 0.0, 0.0),   Vector3D(1.0, 0.0, 0.0)]),
        Triangle([Vector3D(0.0, 0.0, 1.0),   Vector3D(1.0, 0.0, 0.0),   Vector3D(1.0, 0.0, 1.0)])
    ])


width, height = 960, 540
angle = 0
near = 0.1
far = 1000.0
fov = 90.0
aspect_ratio = height / width
fov_rad = 1.0 / math.tan(fov * 0.5 / 180 * math.pi)
camera = Vector3D(0.0, 0.0, 0.0)
triangles_to_draw = []


def load_obj_file(file_name):
    if not exists(file_name):
        print("File "+file_name+" does not exist")
        return False
    file = open(file_name, 'r')
    vertices_list = []
    triangle_list = []
    count = 0
    for line in file:
        count += 1
        if line[0] == 'v':
            line = line[2:-2]
            vertices_split = line.split(' ')
            vertex = Vector3D(float(vertices_split[0]), float(vertices_split[1]), float(vertices_split[2]))
            vertices_list.append(vertex)
        if line[0] == 'f':
            line = line[2:-1]
            triangle_split = line.split(' ')
            triangle = Triangle([vertices_list[int(triangle_split[0])-1], vertices_list[int(triangle_split[1])-1], vertices_list[int(triangle_split[2])-1]])
            triangle_list.append(triangle)
    file.close()
    return Mesh(triangle_list)


def multiply_matrix_vector(o, n, m):
    n.x = o.x * m[0][0] + o.y * m[1][0] + o.z * m[2][0] + m[3][0]
    n.y = o.x * m[0][1] + o.y * m[1][1] + o.z * m[2][1] + m[3][1]
    n.z = o.x * m[0][2] + o.y * m[1][2] + o.z * m[2][2] + m[3][2]
    w = o.x * m[0][3] + o.y * m[1][3] + o.z * m[2][3] + m[3][3]

    if w != 0:
        n.x /= w
        n.y /= w
        n.z /= w


def dot_product(vector1, vector2):
    return vector1.x * vector2.x + vector1.y * vector2.y + vector1.z * vector2.z


def normalize_vector(vector):
    length = math.sqrt(vector.x * vector.x + vector.y * vector.y + vector.z * vector.z)
    vector.x /= length; vector.y /= length; vector.z /= length


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def triangle_midpoint(triangle):
    return (triangle.points[0].z + triangle.points[1].z + triangle.points[2].z) / 3.0


def draw_triangle(canvas, triangle, color):
    canvas.create_line(triangle.points[0].x, triangle.points[0].y, triangle.points[1].x, triangle.points[1].y, fill=color)
    canvas.create_line(triangle.points[1].x, triangle.points[1].y, triangle.points[2].x, triangle.points[2].y, fill=color)
    canvas.create_line(triangle.points[2].x, triangle.points[2].y, triangle.points[0].x, triangle.points[0].y, fill=color)


def fill_triangle(canvas, triangle, color):
    canvas.create_polygon(triangle.points[0].x, triangle.points[0].y,
                          triangle.points[1].x, triangle.points[1].y,
                          triangle.points[2].x, triangle.points[2].y, fill=color)


def draw_mesh(canvas, current_object):
    location = current_object.loc
    rotation = current_object.rot
    scale = current_object.scale
    mesh = current_object.mesh
    if not (mesh is None):
        angle_rad = angle*(math.pi/180)
        mat_rot_x = [
            [1, 0, 0, 0],
            [0, math.cos(angle_rad*rotation.x), math.sin(angle_rad*rotation.x), 0],
            [0, -math.sin(angle_rad*rotation.x), math.cos(angle_rad*rotation.x), 0],
            [0, 0, 0, 1]]
        mat_rot_y = [
            [math.cos(angle_rad*rotation.y), 0, math.sin(angle_rad*rotation.y), 0],
            [0, 1, 0, 0],
            [-math.sin(angle_rad*rotation.y), 0, math.cos(angle_rad*rotation.y), 0],
            [0, 0, 0, 1]]
        mat_rot_z = [
            [math.cos(angle_rad*rotation.z), math.sin(angle_rad*rotation.z), 0, 0],
            [-math.sin(angle_rad*rotation.z), math.cos(angle_rad*rotation.z), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]
        projection_matrix = [
            [aspect_ratio * fov_rad, 0, 0, 0],
            [0, fov_rad, 0, 0],
            [0, 0, far / (far - near), 1.0],
            [0, 0, (-far * near) / (far - near), 0]]

        for mesh_triangle in mesh.triangles:
            triangle_projected = copy.deepcopy(mesh_triangle)
            triangle_scaled = copy.deepcopy(mesh_triangle)
            triangle_rotated_x = copy.deepcopy(mesh_triangle)
            triangle_rotated_xy = copy.deepcopy(mesh_triangle)
            triangle_rotated_xyz = copy.deepcopy(mesh_triangle)

            triangle_scaled.points[0].x *= scale.x
            triangle_scaled.points[1].x *= scale.x
            triangle_scaled.points[2].x *= scale.x
            triangle_scaled.points[0].y *= scale.y
            triangle_scaled.points[1].y *= scale.y
            triangle_scaled.points[2].y *= scale.y
            triangle_scaled.points[0].z *= scale.z
            triangle_scaled.points[1].z *= scale.z
            triangle_scaled.points[2].z *= scale.z

            multiply_matrix_vector(triangle_scaled.points[0], triangle_rotated_x.points[0], mat_rot_x)
            multiply_matrix_vector(triangle_scaled.points[1], triangle_rotated_x.points[1], mat_rot_x)
            multiply_matrix_vector(triangle_scaled.points[2], triangle_rotated_x.points[2], mat_rot_x)

            multiply_matrix_vector(triangle_rotated_x.points[0], triangle_rotated_xy.points[0], mat_rot_y)
            multiply_matrix_vector(triangle_rotated_x.points[1], triangle_rotated_xy.points[1], mat_rot_y)
            multiply_matrix_vector(triangle_rotated_x.points[2], triangle_rotated_xy.points[2], mat_rot_y)

            multiply_matrix_vector(triangle_rotated_xy.points[0], triangle_rotated_xyz.points[0], mat_rot_z)
            multiply_matrix_vector(triangle_rotated_xy.points[1], triangle_rotated_xyz.points[1], mat_rot_z)
            multiply_matrix_vector(triangle_rotated_xy.points[2], triangle_rotated_xyz.points[2], mat_rot_z)

            triangle_translated = copy.deepcopy(triangle_rotated_xyz)
            triangle_translated.points[0].x += location.x
            triangle_translated.points[1].x += location.x
            triangle_translated.points[2].x += location.x
            triangle_translated.points[0].y += -location.y
            triangle_translated.points[1].y += -location.y
            triangle_translated.points[2].y += -location.y
            triangle_translated.points[0].z += location.z
            triangle_translated.points[1].z += location.z
            triangle_translated.points[2].z += location.z

            multiply_matrix_vector(triangle_translated.points[0], triangle_projected.points[0], projection_matrix)
            multiply_matrix_vector(triangle_translated.points[1], triangle_projected.points[1], projection_matrix)
            multiply_matrix_vector(triangle_translated.points[2], triangle_projected.points[2], projection_matrix)

            normal = Vector3D()
            line1 = Vector3D()
            line2 = Vector3D()
            line1.x = triangle_translated.points[1].x - triangle_translated.points[0].x
            line1.y = triangle_translated.points[1].y - triangle_translated.points[0].y
            line1.z = triangle_translated.points[1].z - triangle_translated.points[0].z

            line2.x = triangle_translated.points[2].x - triangle_translated.points[0].x
            line2.y = triangle_translated.points[2].y - triangle_translated.points[0].y
            line2.z = triangle_translated.points[2].z - triangle_translated.points[0].z

            normal.x = line1.y * line2.z - line1.z * line2.y
            normal.y = line1.z * line2.x - line1.x * line2.z
            normal.z = line1.x * line2.y - line1.y * line2.x
            normalize_vector(normal)

            camera_relation = Vector3D()
            camera_relation.x = triangle_translated.points[0].x - camera.x
            camera_relation.y = triangle_translated.points[0].y - camera.y
            camera_relation.z = triangle_translated.points[0].z - camera.z

            if dot_product(normal, camera_relation) < 0:
                light_direction = Vector3D(0.0, 0.0, -1.0)
                normalize_vector(light_direction)
                light_amount = dot_product(normal, light_direction)
                if light_amount > 0:
                    rgb_lit = (int(current_object.color[0]*light_amount),
                               int(current_object.color[1]*light_amount),
                               int(current_object.color[2]*light_amount))
                else:
                    rgb_lit = (0, 0, 0)

                triangle_projected.points[0].x += 1.0
                triangle_projected.points[0].y += 1.0
                triangle_projected.points[1].x += 1.0
                triangle_projected.points[1].y += 1.0
                triangle_projected.points[2].x += 1.0
                triangle_projected.points[2].y += 1.0

                triangle_projected.points[0].x *= 0.5 * float(width)
                triangle_projected.points[0].y *= 0.5 * float(height)
                triangle_projected.points[1].x *= 0.5 * float(width)
                triangle_projected.points[1].y *= 0.5 * float(height)
                triangle_projected.points[2].x *= 0.5 * float(width)
                triangle_projected.points[2].y *= 0.5 * float(height)

                triangle_projected.rgb = rgb_lit

                triangles_to_draw.append(triangle_projected)
        triangles_to_draw.sort(reverse=True, key=triangle_midpoint)
        for triangle in triangles_to_draw:
            fill_triangle(canvas, triangle, rgb_to_hex(triangle.rgb))
            #draw_triangle(canvas, triangle, 'black')
        triangles_to_draw.clear()


def rotate_mesh(canvas, object_list, degrees):
    global angle
    angle += degrees
    canvas.delete('all')
    for current_object in object_list:
        draw_mesh(canvas, current_object)
    canvas.master.after(5, rotate_mesh, canvas, object_list, 1)


def main():
    root = Tk()
    window = Canvas(root, width=width, height=height)
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    win_x = int(screen_width/2 - width/2)
    win_y = int(screen_height/2 - height/2)
    root.geometry(str(width)+"x"+str(height)+"+"+str(win_x)+"+"+str(win_y))
    window.configure(background='#a1a1a1')
    window.pack()

    cube1 = Object(Vector3D(1.0, 0.0, 6.0), Vector3D(0.2, 0.4, 0.6), None, (87, 151, 255), Shapes.cube)
    cube2 = Object(Vector3D(-1.0, 0.0, 3.0), Vector3D(0.4, 0.2, 0.6), None, (230, 18, 18), Shapes.cube)
    pyramid = Object(Vector3D(-5.0, 0.0, 6.0), Vector3D(1.0, 0.5, 0.5), None, (230, 18, 18), Shapes.rectangular_pyramid)
    sphere = Object(Vector3D(-2.0, 2.0, 4.0), Vector3D(0.5, 0.2, 0.7), None, (54, 186, 39), load_obj_file('sphere.obj'))
    ring = Object(Vector3D(-2.0, 0.0, 4.0), Vector3D(0.5, 0.2, 0.7), None, (54, 186, 39), load_obj_file('ring.obj'))

    object_list = [sphere, cube2]

    for current_object in object_list:
        draw_mesh(window, current_object)

    root.after(20, rotate_mesh, window, object_list, 1)

    root.mainloop()


if __name__ == '__main__':
    main()
