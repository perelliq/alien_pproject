import hashlib

from generativepy.drawing import make_image, setup
from generativepy.geometry import Polygon
from generativepy.color import Color
from scipy.spatial import Voronoi

import random

random.seed(40)
SIZE = 4000
POINTS = random.randint(8000, 8500)
COLORS = ["e0b0ff", "9999ff", "f78fa7", "ff4e33", "ffa742", "d1cd4d"]

points = [[random.randrange(SIZE), random.randrange(SIZE)]
          for i in range(POINTS)]
points.append([-SIZE * 3, -SIZE * 3])
points.append([-SIZE * 3, SIZE * 4])
points.append([SIZE * 4, -SIZE * 3])
points.append([SIZE * 4, SIZE * 4])


def draw(ctx, pixel_width, pixel_height, frame_no, frame_count):
    setup(ctx, pixel_width, pixel_height, background=Color(random.random()))
    voronoi = Voronoi(points)
    voronoi_vertices = voronoi.vertices

    for region in voronoi.regions:
        if -1 not in region:
            l = random.randint(2, 8)
            polygon = [voronoi_vertices[i] for i in region]
            ctx.set_source_rgba(random.random(), random.random(), random.random(), 0.7)
            ctx.fill()
            Polygon(ctx).of_points(polygon).stroke(line_width=0,
                                                   pattern=Color(random.random(), random.random(), random.random(), 0.3))


def make_hash(name):
    hash_object = hashlib.md5(name.encode())
    hash_string = hash_object.hexdigest()[-8::]
    return hash_string


def save_pic(name):
    image = "static/img/" + name + ".png"
    make_image(image, draw, SIZE, SIZE)


save_pic("bg_1")
