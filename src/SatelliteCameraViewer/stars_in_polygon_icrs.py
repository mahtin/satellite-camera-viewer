"""
stars_in_polygon_icrs - Spherical point-in-polygon test.
"""

import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

def stars_in_polygon_icrs(stars: list[SkyCoord], poly_ra_dec: list[tuple[float,float]]):
    """
    stars_in_polygon_icrs() - Spherical point-in-polygon test.

    :param stars: An array of stars (in ICRS) to search.
    :type stars: list[SkyCoord]
    :param poly_ra_dec: Nx2 array of polygon vertices (ra, dec) in degrees (ICRS).
    :type poly_ra_dec: list[tuple[float,float]]

    :return: A boolean mask of stars inside the polygon.
    :rtype: A list of bool values

    """

    # Convert stars to unit vectors
    x = stars.icrs.cartesian.x.value
    y = stars.icrs.cartesian.y.value
    z = stars.icrs.cartesian.z.value
    star_vecs = np.vstack([x, y, z]).T

    # Convert polygon vertices to unit vectors
    poly = SkyCoord(ra=[p[0] for p in poly_ra_dec]*u.deg,
                    dec=[p[1] for p in poly_ra_dec]*u.deg,
                    frame="icrs")
    px = poly.cartesian.x.value
    py = poly.cartesian.y.value
    pz = poly.cartesian.z.value
    poly_vecs = np.vstack([px, py, pz]).T

    # Close polygon
    poly_vecs = np.vstack([poly_vecs, poly_vecs[0]])

    # Compute spherical winding number for each star
    inside = np.zeros(len(stars), dtype=bool)

    for i, s in enumerate(star_vecs):
        total_angle = 0.0
        for j in range(len(poly_vecs)-1):
            a = poly_vecs[j]
            b = poly_vecs[j+1]

            # Compute angle between edges as seen from star
            va = a - s
            vb = b - s
            va /= np.linalg.norm(va)
            vb /= np.linalg.norm(vb)

            dot = np.clip(np.dot(va, vb), -1.0, 1.0)
            angle = np.arccos(dot)

            # Signed angle using triple product
            sign = np.sign(np.dot(s, np.cross(a, b)))
            total_angle += sign * angle

        # Inside if winding number ≈ ±2π
        inside[i] = np.abs(total_angle) > np.pi

    return inside
