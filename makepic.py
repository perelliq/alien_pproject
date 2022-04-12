import hashlib

from generativepy.drawing import make_image, setup
from generativepy.geometry import Polygon
from generativepy.color import Color
from scipy.spatial import Voronoi

import random

SIZE = 400
POINTS = random.randint(2, 100)

# random.seed(40)
points = [[random.randrange(SIZE), random.randrange(SIZE)]
          for i in range(POINTS)]
points.append([-SIZE * 3, -SIZE * 3])
points.append([-SIZE * 3, SIZE * 4])
points.append([SIZE * 4, -SIZE * 3])
points.append([SIZE * 4, SIZE * 4])


def draw(ctx, pixel_width, pixel_height, frame_no, frame_count):
    setup(ctx, pixel_width, pixel_height, background=Color(1))
    voronoi = Voronoi(points)
    voronoi_vertices = voronoi.vertices

    for region in voronoi.regions:
        if -1 not in region:
            polygon = [voronoi_vertices[p] for p in region]
            Polygon(ctx).of_points(polygon).stroke(line_width=2)


def make_hash(name):
    hash_object = hashlib.md5(name.encode())
    hash_string = hash_object.hexdigest()[-8::]
    return hash_string


make_image("static/img/voronoi_1.png", draw, SIZE, SIZE)
