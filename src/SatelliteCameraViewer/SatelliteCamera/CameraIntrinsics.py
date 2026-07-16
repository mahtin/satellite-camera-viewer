"""
CameraIntrinsics.py

# Camera model
"""

import math
from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation as R
from astropy.time import Time
from astropy.coordinates import SkyCoord, GCRS
import astropy.units as u

from .BrownConradyCoeffs import BrownConradyCoeffs
from .CameraAttitude import CameraAttitude
from .SatelliteOrbit import SatelliteOrbit

class CameraIntrinsicsError(Exception):
    """ CameraIntrinsicsError """

@dataclass
class CameraIntrinsics:
    """ CameraIntrinsics """
    focal_length_mm: float                 # focal length (mm)
    sensor_size_x_mm: float                # sensor width (mm)
    sensor_size_y_mm: float                # sensor height (mm)
    nx: int                                # pixels in x
    ny: int                                # pixels in y
    cx: float = None                       # principal point x (pixels)
    cy: float = None                       # principal point y (pixels)
    bcc: BrownConradyCoeffs = None         # radial/tangential distortion (Brown-Conrady model)
    sensor_to_lens_mm: float = None        # distance from sensor to lens principal plane (UNUSED PRESENTLY)

    def __post_init__(self):
        """ CameraIntrinsics """
        if self.cx is None:
            self.cx = self.nx / 2.0
        if self.cy is None:
            self.cy = self.ny / 2.0
        if self.bcc is None:
            # The default value for Brown-Conrady lens distortion coefficients (k1 ,k2 ,p1 ,p2 ,k3)
            # are typically zero for all parameters, representing an ideal, undistorted lens.
            self.bcc = BrownConradyCoeffs(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)

        # For a pinhole model, focal_length_mm == sensor_to_lens_mm
        # But we keep them separate so real lenses can be modeled.
        self._effective_focal_length_mm = self.focal_length_mm

    def __str__(self):
        """ __str__ """
        return 'Camera[sensor: %.1fx%.1f mm with %dx%d pixels @ focal length: %d mm]' % (self.sensor_size_x_mm, self.sensor_size_y_mm, self.nx, self.ny, self.focal_length_mm)

    @property
    def pixel_size_x_mm(self):
        """ pixel_size_x_mm - x size of sensor in mm """
        return self.sensor_size_x_mm / self.nx

    @property
    def pixel_size_y_mm(self):
        """ pixel_size_y_mm - y size of sensor in mm """
        return self.sensor_size_y_mm / self.ny

    @property
    def aspect_ratio(self):
        """ aspect_ratio - return sensor aspect ratio """
        return self.sensor_size_x_mm / self.sensor_size_y_mm

    @property
    def fov_x_deg(self):
        """ fov_x_deg - return x axis FOV in degrees """
        return 2 * math.degrees(np.arctan((self.sensor_size_x_mm / 2) / self.focal_length_mm))

    @property
    def fov_y_deg(self):
        """ fov_y_deg - return y axis FOV in degrees """
        return 2 * math.degrees(np.arctan((self.sensor_size_y_mm / 2) / self.focal_length_mm))

    @property
    def fov_diag_deg(self):
        """ fov_diag_deg - return diagonal axis FOV in degrees """
        diag = np.sqrt(self.sensor_size_x_mm**2 + self.sensor_size_y_mm**2)
        return 2 * math.degrees(np.arctan((diag / 2) / self.focal_length_mm))

    def _pixel_to_sensor_mm(self, px: float, py: float):
        """
        Convert pixel coordinates to sensor-plane coordinates (mm),
        with origin at principal point.
        """
        x_mm = (px - self.cx) * self.pixel_size_x_mm
        y_mm = (py - self.cy) * self.pixel_size_y_mm
        return x_mm, y_mm

    def _sensor_mm_to_pixel(self, x_mm: float, y_mm: float):
        """
        Convert sensor-plane coordinates (mm) coordinates to pixels,
        with origin at principal point.
        """
        px = self.cx + x_mm / self.pixel_size_x_mm
        py = self.cy + y_mm / self.pixel_size_y_mm
        return px, py

    def _apply_distortion(self, x_mm: float, y_mm: float):
        """
        Apply radial + tangential distortion to sensor-plane coordinates.
        Model: Brown-Conrady in normalized coordinates.
        """
        # Normalize by focal length to get dimensionless coords
        x = x_mm / self._effective_focal_length_mm
        y = y_mm / self._effective_focal_length_mm

        r2 = x * x + y * y
        r4 = r2 * r2
        r6 = r4 * r2

        radial = 1 + self.bcc.k1 * r2 + self.bcc.k2 * r4 + self.bcc.k3 * r6
        x_radial = x * radial
        y_radial = y * radial

        x_tangential = 2 * self.bcc.p1 * x * y + self.bcc.p2 * (r2 + 2 * x * x)
        y_tangential = self.bcc.p1 * (r2 + 2 * y * y) + 2 * self.bcc.p2 * x * y

        x_dist = x_radial + x_tangential
        y_dist = y_radial + y_tangential

        # Back to mm
        return x_dist * self._effective_focal_length_mm, y_dist * self._effective_focal_length_mm

    def _pixel_to_camera_ray(self, px: float, py: float, use_distortion=True):
        """
        Pixel -> unit direction vector in camera frame.
        Camera frame convention:
        - +Z: optical axis (forward)
        - +X: to the right
        - +Y: up
        """
        x_mm, y_mm = self._pixel_to_sensor_mm(px, py)

        if use_distortion:
            x_mm, y_mm = self._apply_distortion(x_mm, y_mm)

        # Ray direction in camera coordinates
        # Sensor is at z = 0, lens is at z = +focal-length
        ray = np.array([x_mm, y_mm, self._effective_focal_length_mm], dtype=float)
        return ray / np.linalg.norm(ray)

    # =========================
    # Pixel -> RA/Dec
    # =========================

    def pixel_to_radec(self, px: float, py: float, attitude: CameraAttitude, observed_time):
        """
        Convert a pixel coordinate to RA/Dec using:
        - Correct camera geometry
        - Correct camera -> ECI rotation
        - Correct TEME -> GCRS conversion
        """

        # 1. Pixel -> camera-frame ray
        v_cam = self._pixel_to_camera_ray(px, py, use_distortion=True)

        # 2. Camera frame -> ECI (GCRS) using quaternion
        rot = R.from_quat(attitude.quat_cam_to_eci, scalar_first=True)
        v_eci = rot.apply(v_cam)
        v_eci /= np.linalg.norm(v_eci)

        # 4. Convert ECI direction vector -> RA/Dec using SkyCoord
        #    (SkyCoord handles quadrant, wrap, and pole behavior correctly)
        x, y, z = v_eci
        sc = SkyCoord(x=x, y=y, z=z, representation_type='cartesian', frame='gcrs', obstime=observed_time.t)
        ra_deg = sc.spherical.lon.deg % 360.0
        dec_deg = sc.spherical.lat.deg
        return ra_deg, dec_deg

    # =========================
    # Pixels (from the box) -> RA/Dec
    # =========================

    def sensor_to_radec(self, attitude: CameraAttitude, observed_time, nsteps=3):
        """ sensor_to_radec """
        pixels = {}
        for py in range(0, self.ny+1, int(self.ny/nsteps)):
            for px in range(0, self.nx+1, int(self.nx/nsteps)):
                if px >= self.nx:
                    px = self.nx-1
                if py >= self.ny:
                    py = self.ny-1
                ra_deg, dec_deg = self.pixel_to_radec(px, py, attitude, observed_time)
                pixels[(px,py)] = (ra_deg, dec_deg)
        return pixels

    # =========================
    # Pixel -> RA/Dec
    # =========================

    def pixel_to_radec_and_vector(self, px: float, py: float, attitude: CameraAttitude, observed_time, sat_orbit: SatelliteOrbit = None):
        """
        Convert a pixel coordinate to RA/Dec and return satellite vector
        """

        # 3. If satellite orbit is provided, convert TEME -> GCRS
        if sat_orbit is not None:
            r_teme_km = sat_orbit.eci_position_vector(observed_time)
            r_gcrs_km = CameraAttitude.teme_to_gcrs_vector(r_teme_km, observed_time)
        else:
            r_gcrs_km = None

        ra_deg, dec_deg = self.pixel_to_radec(px, py, attitude, observed_time)
        return ra_deg, dec_deg, r_gcrs_km

    # =========================
    # RA/Dec -> Pixel
    # =========================

    def radec_to_pixel(self, ra_deg:float, dec_deg:float, attitude: CameraAttitude, observed_time):
        """
        Convert an RA/Dec (ICRS) direction into pixel coordinates (px, py)
        using the camera's orientation quaternion (w, x, y, z).

        Raises CameraIntrinsicsError if the direction is outside the camera FOV.
        """

        # 1. Convert RA/Dec to ICRS SkyCoord
        target_icrs = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
        # 2. Convert to GCRS at observed_time (same as pixel_to_radec)
        target_gcrs = target_icrs.transform_to(GCRS(obstime=observed_time.t))
        # 4. Convert target direction into a 3D unit vector (GCRS)
        t_vec = np.array([
            target_gcrs.cartesian.x.value,
            target_gcrs.cartesian.y.value,
            target_gcrs.cartesian.z.value
        ])

        # 3. Extract ICRS→camera quaternion
        rot = R.from_quat(attitude.quat_cam_to_eci, scalar_first=True).inv()        # (note the .inv() it's important)
        # 5. Rotate into camera frame
        v_cam = rot.apply(t_vec)

        # 6. Reject stars behind the camera
        if v_cam[2] <= 0:
            ## print('radec_to_pixel() [%.1f,%.1f] %-30s %s' % (ra_deg, dec_deg, attitude.quat_cam_to_eci, v_cam))
            raise CameraIntrinsicsError('Direction is behind the camera') from None

        # 7. Pinhole projection onto sensor plane (use self._effective_focal_length_mm)
        scale = self._effective_focal_length_mm / v_cam[2]
        x_mm = v_cam[0] * scale
        y_mm = v_cam[1] * scale

        # 8. Convert mm to pixel coordinates
        px, py = self._sensor_mm_to_pixel(x_mm, y_mm)

        ## print('radec_to_pixel() [%.1f,%.1f] %-30s %-30s ; scale=%.3f mm=[%d,%d] pixel=[%d,%d]' % (ra_deg, dec_deg, attitude.quat_cam_to_eci, v_cam, scale, x_mm, y_mm, px, py))

        # 9. Check bounds
        if px < 0 or px >= self.nx or py < 0 or py >= self.ny:
            raise CameraIntrinsicsError('Direction is outside the camera field of view') from None
        return int(px), int(py)
