"""
CameraFOV.py

Field-of-view box (RA/Dec polygon)
"""

import numpy as np

from scipy.spatial import ConvexHull
from astropy.coordinates import SkyCoord
import astropy.units as u
from spherical_geometry import polygon as sgeom
try:
    import healpy as hp        # pylint: disable=C0415
except ModuleNotFoundError:
    hp = None

from .CameraIntrinsics import CameraIntrinsics
from .CameraAttitude import CameraAttitude

class CameraFOVError(Exception):
    """ CameraFOVError """

class CameraFOV:
    """ CameraFOV """

    @classmethod
    def camera_fov_radec_box(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time):
        """
        Compute RA/Dec for the four corners of the camera sensor.
        Returns a dict with RA/Dec for each corner and a SkyCoord polygon.
        """

        corners = {
            "top_left":    (0, 0),
            "top_right":   (camera.nx - 1, 0),
            "bottom_right":(camera.nx - 1, camera.ny - 1),
            "bottom_left": (0, camera.ny - 1),
        }

        ra_list = []
        dec_list = []
        results = {}

        for name, (px, py) in corners.items():
            ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
            results[name] = {"ra_deg": ra_deg, "dec_deg": dec_deg}
            ra_list.append(ra_deg)
            dec_list.append(dec_deg)

        # Create a SkyCoord polygon for convenience
        polygon = SkyCoord(
            ra=np.array(ra_list) * u.deg,
            dec=np.array(dec_list) * u.deg,
            frame="gcrs"
        )

        results["polygon"] = polygon
        return results

    @classmethod
    def _safe_spherical_polygon_from_vectors(cls, verts_xyz):
        """
        Create a spherical polygon from 3D unit vectors.
        Uses from_xyz() if available, otherwise falls back
        to a robust spherical-excess implementation.
        """

        # Try modern API (spherical_geometry 1.6.1 in theory)
        if hasattr(sgeom.SphericalPolygon, "from_xyz"):
            return sgeom.SphericalPolygon.from_xyz(verts_xyz)

        # -------------------------------
        # Fallback for older versions
        # -------------------------------
        # verts_xyz: Nx3 array of unit vectors in order
        verts = np.asarray(verts_xyz)
        n = len(verts)

        # Normalize all vertices
        verts = verts / np.linalg.norm(verts, axis=1)[:, None]

        # Compute internal angles
        angles = []
        for i in range(n):
            a = verts[i - 1]
            b = verts[i]
            c = verts[(i + 1) % n]

            # Compute angle ABC using atan2 formulation (more stable)
            ab = np.cross(b, a)
            cb = np.cross(b, c)

            # Normalize
            ab /= np.linalg.norm(ab)
            cb /= np.linalg.norm(cb)

            # Angle between the two tangent vectors
            dot = np.clip(np.dot(ab, cb), -1.0, 1.0)
            angle = np.arccos(dot)
            angles.append(angle)

        # Spherical excess
        E = np.sum(angles) - (n - 2) * np.pi

        # Ensure positive area (correct orientation)
        E = abs(E)

        # Dummy polygon object
        class FallbackPoly:
            """ FallbackPoly """
            def area(self):
                """ area """
                return E

        return FallbackPoly()

    @classmethod
    def camera_fov_solid_angle(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time):
        """
        Compute the solid angle of the camera FOV in steradians
        using a robust 3D spherical polygon method.
        """

        # Corner pixels
        corners = [
            (0, 0),
            (camera.nx - 1, 0),
            (camera.nx - 1, camera.ny - 1),
            (0, camera.ny - 1),
        ]

        # Convert each corner to a 3D GCRS unit vector
        verts = []
        for px, py in corners:
            ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
            sc = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame="gcrs")
            verts.append(sc.cartesian.xyz.value)

        verts = np.array(verts)

        # Build spherical polygon from 3D vertices
        sph_poly = cls._safe_spherical_polygon_from_vectors(verts)

        # Return area in steradians
        return sph_poly.area()

    # =========================
    # FOV angular width/height and solid angle
    # =========================

    @classmethod
    def camera_fov_angular_width_height(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time):
        """
        Compute:
        - Angular width and height of the camera FOV
        - Approximate solid angle (steradians) using a spherical polygon area
        """

        # Center pixel
        cx = (camera.nx - 1) / 2.0
        cy = (camera.ny - 1) / 2.0

        # Center RA/Dec
        # ra_c_deg, dec_c_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
        # center = SkyCoord(ra=ra_c_deg * u.deg, dec=dec_c_deg * u.deg, frame="gcrs")

        # Horizontal FOV: center vs midpoints of left/right edges
        ra_l_deg, dec_l_deg = camera.pixel_to_radec(0, cy, attitude, observed_time)
        ra_r_deg, dec_r_deg = camera.pixel_to_radec(camera.nx - 1, cy, attitude, observed_time)
        left = SkyCoord(ra=ra_l_deg * u.deg, dec=dec_l_deg * u.deg, frame="gcrs")
        right = SkyCoord(ra=ra_r_deg * u.deg, dec=dec_r_deg * u.deg, frame="gcrs")

        width = left.separation(right)  # Angle object

        # Vertical FOV: center vs midpoints of top/bottom edges
        ra_t_deg, dec_t_deg = camera.pixel_to_radec(cx, 0, attitude, observed_time)
        ra_b_deg, dec_b_deg = camera.pixel_to_radec(cx, camera.ny - 1, attitude, observed_time)
        top = SkyCoord(ra=ra_t_deg * u.deg, dec=dec_t_deg * u.deg, frame="gcrs")
        bottom = SkyCoord(ra=ra_b_deg * u.deg, dec=dec_b_deg * u.deg, frame="gcrs")

        height = top.separation(bottom)

        # Use the existing FOV box for a spherical polygon area
        # box = cls.camera_fov_radec_box(camera, attitude, observed_time)
        # poly = box["polygon"]  # SkyCoord of 4 corners

        return (
            width,               # astropy Angle
            height              # astropy Angle
        )


    # =========================
    # Convex hull RA/Dec boundary (for distorted sensors)
    # =========================

    @classmethod
    def camera_fov_convex_hull(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time, border_step: int = 100):
        """
        Sample the border of the sensor and compute a convex hull on the sphere.
        Returns:
        - hull_coords: SkyCoord of hull vertices (in order)
        - hull: ConvexHull object in 3D unit-vector space
        """

        border_points = []

        # Top and bottom edges
        for px in range(0, camera.nx, border_step):
            for py in [0, camera.ny - 1]:
                ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
                border_points.append((ra_deg, dec_deg))

        # Left and right edges
        for py in range(0, camera.ny, border_step):
            for px in [0, camera.nx - 1]:
                ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
                border_points.append((ra_deg, dec_deg))

        border_coords = SkyCoord(
            ra=[p[0] for p in border_points] * u.deg,
            dec=[p[1] for p in border_points] * u.deg,
            frame="gcrs",
        )

        # Convert to 3D unit vectors for convex hull
        x = np.cos(border_coords.dec.radian) * np.cos(border_coords.ra.radian)
        y = np.cos(border_coords.dec.radian) * np.sin(border_coords.ra.radian)
        z = np.sin(border_coords.dec.radian)
        pts = np.vstack([x, y, z]).T

        hull = ConvexHull(pts)

        # Hull vertices in RA/Dec order
        hull_pts = pts[hull.vertices]
        hull_ra = np.arctan2(hull_pts[:, 1], hull_pts[:, 0])
        hull_dec = np.arcsin(hull_pts[:, 2])

        hull_coords = SkyCoord(
            ra=hull_ra * u.rad,
            dec=hull_dec * u.rad,
            frame="gcrs",
        )

        return hull_coords, hull

    # =========================
    # HEALPix mask for camera footprint
    # =========================

    @classmethod
    def _spherical_polygon_contains(cls, points_xyz, poly_xyz):
        """
        Vectorized spherical polygon containment test.
        points_xyz: (N,3) array of unit vectors
        poly_xyz:   (M,3) array of polygon vertices (unit vectors), ordered CCW

        Returns: boolean array of length N
        """

        # Number of points and polygon edges
        # N = points_xyz.shape[0]
        # M = poly_xyz.shape[0]

        # Roll polygon vertices to get edges
        v1 = poly_xyz
        v2 = np.roll(poly_xyz, -1, axis=0)

        # Edge normals (M,3)
        edge_normals = np.cross(v1, v2)
        edge_normals /= np.linalg.norm(edge_normals, axis=1, keepdims=True)

        # Dot product of each point with each edge normal
        # Result shape: (N, M)
        dots = points_xyz @ edge_normals.T

        # Inside polygon if dot >= 0 for all edges
        return np.all(dots >= 0, axis=1)

    @classmethod
    def camera_fov_healpix_mask(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time, nside=64):
        """
        Return HEALPix pixel indices inside the camera FOV.
        Uses 3D spherical polygon for robustness.
        """

        if hp is None:
            raise CameraFOVError('healpy not installed - maybe you are on Windows11?') from None

        # Corner pixels of the sensor
        corners = [
            (0, 0),
            (camera.nx - 1, 0),
            (camera.nx - 1, camera.ny - 1),
            (0, camera.ny - 1),
        ]

        # Convert corners to 3D GCRS unit vectors
        verts_xyz = []
        for px, py in corners:
            ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
            sc = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame="gcrs")
            verts_xyz.append(sc.cartesian.xyz.value)

        verts_xyz = np.array(verts_xyz)

        # Healpy supports 3D polygon queries directly
        pix = hp.query_polygon(nside, verts_xyz, inclusive=True)

        mask = np.zeros(hp.nside2npix(nside), dtype=bool)
        mask[pix] = True

        return mask, pix

    @classmethod
    def camera_fov_border_vectors(cls, camera: CameraIntrinsics, attitude: CameraAttitude, observed_time, border_step=50):
        """
        Sample the full border of the camera sensor and return
        a list of 3D GCRS unit vectors representing the FOV boundary.

        border_step = number of samples per edge (higher for ultra-wide lenses)
        """

        # Build pixel coordinates along the border
        xs_top    = np.linspace(0.0, camera.nx - 1.0, border_step)
        xs_bottom = np.linspace(0.0, camera.nx - 1.0, border_step)
        ys_left   = np.linspace(0.0, camera.ny - 1.0, border_step)
        ys_right  = np.linspace(0.0, camera.ny - 1.0, border_step)

        border_pixels = []

        # Top edge (except last point)
        for x in xs_top[:-1]:
            border_pixels.append((x, 0.0))

        # Right edge (except last point)
        for y in ys_right[0:-1]:
            border_pixels.append((camera.nx - 1.0, y))

        # Bottom edge (except last point)
        for x in xs_bottom[:0:-1]:
            border_pixels.append((x, camera.ny - 1.0))

        # Left edge (all point - hence closing the polygon)
        for y in ys_left[::-1]:
            border_pixels.append((0.0, y))

        # Convert border pixels to a 3D GCRS unit vectors
        ra_list = []
        dec_list = []
        for px, py in border_pixels:
            ra_deg, dec_deg = camera.pixel_to_radec(px, py, attitude, observed_time)
            ra_list.append(ra_deg)
            dec_list.append(dec_deg)

        polygon = SkyCoord(
            ra=np.array(ra_list) * u.deg,
            dec=np.array(dec_list) * u.deg,
            frame="gcrs"
        )

        return polygon
