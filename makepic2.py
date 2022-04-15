import numpy
import matplotlib.pyplot as plot
from scipy.spatial import Voronoi


def create_voronoi(vor, radius=None):
    if vor.points.shape[1] != 2:
        raise ValueError("requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.point.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # for p1, region in enumerate(vor.point_region):
        # vertices = vor.regions[region]:
