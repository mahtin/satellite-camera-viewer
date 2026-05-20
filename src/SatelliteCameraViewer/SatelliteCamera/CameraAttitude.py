"""
CameraAttitude

CameraAttitude model
"""

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation as R
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, TEME, GCRS, CartesianRepresentation
import astropy.units as u

@dataclass
class Attitude:
    """ Attitude """
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0

@dataclass
class Quaternion:
    """
    A satellite quaternion body (or attitude quaternion) is a 4-component mathematical tool
    q = [q0,q1,q2,q3] or q = [s,v]
    used to represent the 3D orientation (attitude) of a satellite's body-fixed frame relative
    to a reference frame.
    https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation
    """
    # There are 2 conventions to order the components in a quaternion:
    # scalar-first order - (w, x, y, z)
    # scalar-last order - (x, y, z, w)
    # We use scaler-first notation form (vs scaler-last or vector-first).
    qw : float = 1.0	# scaler
    qx : float = 0.0	# Imaginary i
    qy : float = 0.0	# Imaginary j
    qz : float = 0.0	# Imaginary k

    def __str__(self):
        """ __str__ """
        return 'Quaternion[%f,%f,%f,%f]' % (self.qx, self.qy, self.qz, self.qw)

    def __array__(self, dtype=None):
        """Allows np.array(instance) to work."""
        return np.array(self.wxyz, dtype=dtype)

    @property
    def wxyz(self):
        return [self.qx, self.qy, self.qz, self.qw]

    @property
    def w(self):
        return self.qw

    @property
    def x(self):
        return self.qx

    @property
    def y(self):
        return self.qy

    @property
    def z(self):
        return self.qz

@dataclass
class CameraAttitude:
    """
    Full attitude model:
    - Satellite orientation in ECI (as quaternion or yaw/pitch/roll)
    - Camera mounting offsets (yaw/pitch/roll)
    - Produces final camera->ECI quaternion
    """

    # Satellite attitude (body -> ECI)
    # Provide either quaternion or yaw/pitch/roll
    sat_quat_body_to_eci: Quaternion = None  # [w, x,y,z]
    sat_attitude: Attitude = None
    cam_attitude: Attitude = None	# Camera mounting offsets (body -> camera)

    def __post_init__(self):
        """ CameraAttitude """

        # don't do this - we need a None value here if not passed
        #if self.sat_attitude is None:
        #    self.sat_attitude = Attitude()

        # 1. Satellite attitude
        if self.sat_quat_body_to_eci is not None:
            R_sat = R.from_quat(self.sat_quat_body_to_eci, scalar_first=True)
        elif self.sat_attitude is not None:
            # Aerospace sequence: yaw (Z), pitch (Y), roll (X)
            R_sat = R.from_euler('ZYX', [self.sat_attitude.yaw_deg, self.sat_attitude.pitch_deg, self.sat_attitude.roll_deg], degrees=True)
        else:
            raise ValueError("Must provide either satellite quaternion or yaw/pitch/roll")

        # allow default camera attitude (of 0,0,0) with respect to the satellite
        if self.cam_attitude is None:
            self.cam_attitude = Attitude()

        # 2. Camera mounting rotation (body -> camera)
        R_cam = R.from_euler("ZYX", [self.cam_attitude.yaw_deg, self.cam_attitude.pitch_deg, self.cam_attitude.roll_deg], degrees=True)

        # 3. Final camera->ECI rotation
        # camera->ECI = body->ECI degree camera->body
        R_cam_to_eci = R_sat * R_cam

        # always scalar_first=False (i.e. default)
        self._quat_cam_to_eci = R_cam_to_eci.as_quat(scalar_first=True)

    @property
    def quat_cam_to_eci(self):
        """ quat_cam_to_eci """
        return self._quat_cam_to_eci

    def cam_to_eci(self, v_cam: np.ndarray) -> np.ndarray:
        """ cam_to_eci """
        rot = R.from_quat(self._quat_cam_to_eci, scalar_first=True)
        return rot.apply(v_cam)

    @classmethod
    def quaternion_wxyz(cls, qw:float=1.0, qx:float=0.0, qy:float=0.0, qz:float=0.0) -> Quaternion:
        """ quaternion """
        return Quaternion(qw, qx, qy, qz)

    # =========================
    # Automatic Nadir-Pointing Quaternion
    # Nadir = direction from satellite toward Earth center.
    # We construct a full orthonormal camera frame:
    # +Z_cam = nadir direction
    # +X_cam = perpendicular to orbital plane (or fallback)
    # +Y_cam = completes right-handed frame
    # Then convert that rotation matrix -> quaternion.
    # =========================

    @classmethod
    def quaternion_nadir_pointing(cls, r_eci_km):
        """
        Compute camera->ECI quaternion for nadir pointing.
        r_eci_km: satellite position in ECI (km), shape (3,)

        Returns: quaternion [w, x, y, z]
        """

        # +Z_cam = direction toward Earth center
        z_cam = -r_eci_km / np.linalg.norm(r_eci_km)

        # Choose a reference vector not parallel to z_cam
        ref = np.array([0, 0, 1.0])
        if abs(np.dot(ref, z_cam)) > 0.9:
            ref = np.array([0, 1.0, 0])

        # +X_cam = perpendicular to z_cam
        x_cam = np.cross(ref, z_cam)
        x_cam /= np.linalg.norm(x_cam)

        # +Y_cam = completes right-handed frame
        y_cam = np.cross(z_cam, x_cam)

        # Rotation matrix: columns are camera axes expressed in ECI
        R_cam_to_eci = np.column_stack([x_cam, y_cam, z_cam])

        return R.from_matrix(R_cam_to_eci).as_quat(scalar_first=True)

    # =========================
    # Automatic Velocity-Vector Pointing Quaternion
    # This points the camera optical axis along the velocity direction.
    # +Z_cam = normalized velocity vector
    # +X_cam = perpendicular to velocity and position (orbital normal)
    # +Y_cam = completes right-handed frame
    # =========================

    @classmethod
    def quaternion_velocity_pointing(cls, r_eci_km, v_eci_km_s):
        """
        Compute camera->ECI quaternion for velocity-vector pointing.
        r_eci_km: satellite position in ECI (km)
        v_eci_km_s: satellite velocity in ECI (km/s)

        Returns: quaternion [w, x, y, z]
        """

        # +Z_cam = direction of motion
        z_cam = v_eci_km_s / np.linalg.norm(v_eci_km_s)

        # Orbital normal (for X axis)
        n = np.cross(r_eci_km, v_eci_km_s)
        if np.linalg.norm(n) < 1e-6:
            # Degenerate orbit case: choose fallback
            n = np.array([0, 0, 1.0])

        x_cam = np.cross(n, z_cam)
        x_cam /= np.linalg.norm(x_cam)

        # +Y_cam = completes right-handed frame
        y_cam = np.cross(z_cam, x_cam)

        # Rotation matrix: columns are camera axes expressed in ECI
        R_cam_to_eci = np.column_stack([x_cam, y_cam, z_cam])

        return R.from_matrix(R_cam_to_eci).as_quat(scalar_first=True)

    # =========================
    # Pointing at a Specific RA/Dec Target
    # This function:
    # Converts RA/Dec -> GCRS Cartesian unit vector
    # Builds a right-handed camera frame
    # Produces a quaternion that makes +Z_cam point at the target
    # Avoids singularities near the poles
    # =========================

    @classmethod
    def quaternion_pointing_radec(cls, ra_deg, dec_deg, obs_time):
        """
        Compute camera->ECI quaternion that points +Z_cam at a given RA/Dec target.
        """

        # Target direction in GCRS
        sc = SkyCoord(
            ra=ra_deg * u.deg,
            dec=dec_deg * u.deg,
            frame="gcrs",
            obstime=Time(obs_time)
        )

        # +Z_cam = target direction
        z_cam = sc.cartesian.xyz.value
        z_cam /= np.linalg.norm(z_cam)

        # Choose a reference vector not parallel to z_cam
        ref = np.array([0, 0, 1.0])
        if abs(np.dot(ref, z_cam)) > 0.9:
            ref = np.array([0, 1.0, 0])

        # +X_cam = perpendicular to z_cam
        x_cam = np.cross(ref, z_cam)
        x_cam /= np.linalg.norm(x_cam)

        # +Y_cam = completes right-handed frame
        y_cam = np.cross(z_cam, x_cam)

        # Rotation matrix: columns are camera axes expressed in ECI
        R_cam_to_eci = np.column_stack([x_cam, y_cam, z_cam])

        return R.from_matrix(R_cam_to_eci).as_quat(scalar_first=True)

    # =========================
    # Pointing at a Ground Location (lat/lon)
    # This function:
    # Converts (lat, lon) -> GCRS position of the ground point
    # Computes the direction from satellite -> ground
    # Builds a right-handed camera frame
    # Produces a quaternion that points +Z_cam at the ground location
    # =========================

    @classmethod
    def quaternion_pointing_ground(cls, lat_deg, lon_deg, obs_time, r_sat_gcrs_km):
        """
        Compute camera->ECI quaternion that points +Z_cam at a ground location.
        lat_deg, lon_deg: ground target in degrees
        r_sat_gcrs_km: satellite position in GCRS (km)
        """

        # Ground point in Earth-fixed coordinates
        ground = EarthLocation.from_geodetic(
            lon=lon_deg * u.deg,
            lat=lat_deg * u.deg,
            height=0 * u.m
        )

        # Convert ground point to GCRS
        ground_gcrs = ground.get_gcrs(Time(obs_time))
        r_ground_km = ground_gcrs.cartesian.xyz.to(u.km).value

        # Direction from satellite to ground
        z_cam = r_ground_km - r_sat_gcrs_km
        z_cam /= np.linalg.norm(z_cam)

        # Choose a reference vector not parallel to z_cam
        ref = np.array([0, 0, 1.0])
        if abs(np.dot(ref, z_cam)) > 0.9:
            ref = np.array([0, 1.0, 0])

        # +X_cam = perpendicular to z_cam
        x_cam = np.cross(ref, z_cam)
        x_cam /= np.linalg.norm(x_cam)

        # +Y_cam = completes right-handed frame
        y_cam = np.cross(z_cam, x_cam)

        # Rotation matrix: columns are camera axes expressed in ECI
        R_cam_to_eci = np.column_stack([x_cam, y_cam, z_cam])

        return R.from_matrix(R_cam_to_eci).as_quat(scalar_first=True)

    @classmethod
    def teme_to_gcrs_vector(cls, r_teme_km, obs_time):
        """
        Convert a TEME position vector to GCRS (ECI) using Astropy.
        r_teme_km: (3,) km vector
        Returns: (3,) km vector in GCRS
        """
        teme = TEME(
            CartesianRepresentation(r_teme_km * u.km),
            obstime=Time(obs_time)
        )
        gcrs = teme.transform_to(GCRS(obstime=Time(obs_time)))
        return gcrs.cartesian.xyz.to(u.km).value
