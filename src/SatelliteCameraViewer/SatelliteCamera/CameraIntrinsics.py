"""
CameraIntrinsics.py

# Camera model
"""

from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation as R
from astropy.time import Time
from astropy.coordinates import SkyCoord, GCRS
import astropy.units as u

from .BrownConradyCoeffs import BrownConradyCoeffs
from .CameraAttitude import CameraAttitude
from .CameraSensors import CameraSensor
from .SatelliteOrbit import SatelliteOrbit

class CameraIntrinsicsError(Exception):
    """ CameraIntrinsicsError """

@dataclass
class CameraIntrinsics:
    """ CameraIntrinsics """
    camera_sensor : CameraSensor = None
    focal_length_mm: float = None             # focal length (mm) overriding the base camera sensor

    def __post_init__(self):
        """ CameraIntrinsics """
        if self.camera_sensor is None:
            raise ValueError('camera_sensor cannot be empty')
        if self.focal_length_mm is not None:
            self.camera_sensor.focal_length_mm = self.focal_length_mm

    def __str__(self):
        """ __str__ """
        return str(self.camera_sensor)

    def _pixel_to_camera_ray(self, px: float, py: float, use_distortion=True):
        """
        Pixel -> unit direction vector in camera frame.
        Camera frame convention:
        - +Z: optical axis (forward)
        - +X: to the right
        - +Y: up
        """
        x_mm, y_mm = self.camera_sensor.pixel_to_sensor_mm(px, py, use_distortion)

        # Ray direction in camera coordinates
        # Sensor is at z = 0, lens is at z = +focal-length
        ray = np.array([x_mm, y_mm, self.camera_sensor.effective_focal_length_mm], dtype=float)
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
        for py in range(0, self.camera_sensor.ny+1, int(self.camera_sensor.ny/nsteps)):
            for px in range(0, self.camera_sensor.nx+1, int(self.camera_sensor.nx/nsteps)):
                if px >= self.camera_sensor.nx:
                    px = self.camera_sensor.nx-1
                if py >= self.camera_sensor.ny:
                    py = self.camera_sensor.ny-1
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

        # 7. Pinhole projection onto sensor plane (use self.camera_sensor.effective_focal_length_mm)
        scale = self.camera_sensor.effective_focal_length_mm / v_cam[2]
        x_mm = v_cam[0] * scale
        y_mm = v_cam[1] * scale

        # 8. Convert mm to pixel coordinates
        px, py = self.camera_sensor.sensor_mm_to_pixel(x_mm, y_mm)

        ## print('radec_to_pixel() [%.1f,%.1f] %-30s %-30s ; scale=%.3f mm=[%d,%d] pixel=[%d,%d]' % (ra_deg, dec_deg, attitude.quat_cam_to_eci, v_cam, scale, x_mm, y_mm, px, py))

        # 9. Check bounds
        if px < 0 or px >= self.camera_sensor.nx or py < 0 or py >= self.camera_sensor.ny:
            raise CameraIntrinsicsError('Direction is outside the camera field of view') from None
        return int(px), int(py)
