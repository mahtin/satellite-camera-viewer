"""
Earth.py

# Earth model
"""

from datetime import datetime
import numpy as np
from scipy.spatial.transform import Rotation as R
from astropy.time import Time
from astropy.coordinates import SkyCoord, GCRS, ITRS, get_body, EarthLocation, CartesianRepresentation
import astropy.units as u

from spherical_geometry.polygon import SingleSphericalPolygon

from .SatelliteOrbit import SatelliteOrbit
from .CameraAttitude import CameraAttitude
from .CameraIntrinsics import CameraIntrinsics, CameraIntrinsicsError
from .CameraFOV import CameraFOV

class EarthError(Exception):
    """ EarthError """

class Earth:
    """ Earth """
    def __init__(self, sat_orbit:SatelliteOrbit):
        """
        Earth

        :param sat_orbit: Satellite Orbit
        :type SatelliteOrbit:
        """
        self._sat_orbit = sat_orbit

    def _sat_eci_km(self, obs_time:datetime):
        """ _sat_eci_km """
        return self._sat_orbit.eci_position_vector(obs_time)

    def vector_to_earth_center(self, obs_time:datetime):
        """
        vector_to_earth_center - returns: unit vector pointing from satellite → Earth center
        """
        sat_eci_km = self._sat_eci_km(obs_time)
        v = -np.array(sat_eci_km, dtype=float)
        return v / np.linalg.norm(v)

    def earth_center_direction_icrs(self, obs_time:datetime):
        """ earth_center_direction_icrs """
        sat_eci_km = self._sat_eci_km(obs_time)
        v = -np.array(sat_eci_km)
        v /= np.linalg.norm(v)
        return SkyCoord(x=v[0], y=v[1], z=v[2], representation_type='cartesian', frame='icrs')

    def earth_center_radec_simple(self, obs_time:datetime):
        """ earth_center_radec_simple """
        sat_eci_km = self._sat_eci_km(obs_time)
        v = -np.array(sat_eci_km)
        v /= np.linalg.norm(v)
        ra  = np.degrees(np.arctan2(v[1], v[0])) % 360
        dec = np.degrees(np.arcsin(v[2]))
        return ra, dec

    def earth_center_radec(self, attitude:CameraAttitude, obs_time:datetime):
        """
        sat_eci_km: satellite position in ECI (km)
        quat_cam_to_eci: quaternion rotating camera-frame → ECI-frame
                         format: (w, x, y, z) with scalar_first=True

        Returns:
            (ra_deg, dec_deg) of Earth center in the CAMERA frame
        """
        sat_eci_km = self._sat_eci_km(obs_time)

        quat_cam_to_eci = attitude.quat_cam_to_eci

        # 1. Direction from satellite → Earth center in ECI
        v_eci = -np.array(sat_eci_km, dtype=float)
        v_eci /= np.linalg.norm(v_eci)

        # 2. Build rotation: camera → ECI
        rot_eci = R.from_quat(quat_cam_to_eci, scalar_first=True)

        # 3. Invert to get ECI → camera
        rot_cam = rot_eci.inv()

        # 4. Rotate Earth direction into camera frame
        v_cam = rot_cam.apply(v_eci)

        # 5. Convert camera-frame vector → RA/Dec
        x, y, z = v_cam
        ra_deg  = np.degrees(np.arctan2(y, x)) % 360
        dec_deg = np.degrees(np.arcsin(z))

        return ra_deg, dec_deg

    def earth_angular_radius(self, obs_time:datetime):
        """ earth_angular_radius """
        sat_eci_km = self._sat_eci_km(obs_time)
        sat_dist = np.linalg.norm(np.asarray(sat_eci_km, dtype=float))  # km as float
        return np.degrees(np.arcsin(u.R_earth.to(u.km) / sat_dist))

    def fov_intercept_earth(self, camera:CameraIntrinsics, attitude:CameraAttitude, obs_time:datetime, border_step=None):
        """  fov_intercept_earth """

        t = Time(obs_time)

        # Satellite vector as [x, y, z]
        sat_eci_km = self._sat_eci_km(obs_time)

        def sat_eci_km_to_location(sat_eci_km, obs_time):
            """ sat_eci_km_to_location """
            sat_gcrs = SkyCoord(
                          CartesianRepresentation(
                              x=sat_eci_km[0] * u.km,
                              y=sat_eci_km[1] * u.km,
                              z=sat_eci_km[2] * u.km
                          ),
                          frame=GCRS(obstime=obs_time)
                       )
            sat_itrs = sat_gcrs.transform_to(ITRS(obstime=obs_time))
            sat_location = EarthLocation.from_geocentric(sat_itrs.x.to(u.m), sat_itrs.y.to(u.m), sat_itrs.z.to(u.m))
            # sat_icrs = sat_gcrs.transform_to('icrs')
            # sat_location = EarthLocation.from_geocentric(sat_icrs.x.to(u.m), sat_icrs.y.to(u.m), sat_icrs.z.to(u.m))
            return sat_location

        sat_location = sat_eci_km_to_location(sat_eci_km, obs_time)

        # find earth from satellite location as [x, y, z]
        earth_icrs = get_body('earth', t, location=sat_location).transform_to('icrs')
        earth_vec = earth_icrs.cartesian.xyz.value

        # the camera pointing
        rot_eci = R.from_quat(attitude.quat_cam_to_eci, scalar_first=True)
        rot_cam = rot_eci.inv()   # ECI → camera

        # combine
        earth_cam = rot_cam.apply(earth_vec)

        half_fov = np.deg2rad(camera.fov_diag_deg / 2)
        try:
            angle = np.arccos(np.dot(earth_cam, np.array([0,0,1])))
        except RuntimeWarning:
            # invalid value encountered in arccos
            print('Earth: np.arccos(np.dot(earth_cam, np.array([0,0,1]))) invalid value error with source value earth_cam=%s' % (earth_cam))
            # assume a massive angle - hence this
            raise EarthError('Earth NOT in camera FOV') from None

        if angle > half_fov:
            raise EarthError('Earth NOT in camera FOV') from None

        # TODO - reduced heavily!
        border_step = 8

        print('Earth is in camera FOV')
        fov_cam = CameraFOV.camera_fov_border_vectors(camera, attitude, obs_time, border_step=border_step)
        # fov_cam is a list of SkyCoord objects
        fov_cam_vecs = np.array([[v.cartesian.x.value, v.cartesian.y.value, v.cartesian.z.value] for v in fov_cam])
        fov_icrs = rot_eci.apply(fov_cam_vecs)
        sat_icrs = self._sat_orbit.icrs(obs_time)
        earth_disc_icrs = self._compute_earth_disc_polygon(sat_icrs, obs_time, nsteps=border_step*4)

        def vectors_to_radec(vectors):
            """
            vectors: Nx3 array of unit vectors
            returns: (ra_deg, dec_deg)
            """
            x = vectors[:, 0]
            y = vectors[:, 1]
            z = vectors[:, 2]

            ra  = np.degrees(np.arctan2(y, x)) % 360
            dec = np.degrees(np.arcsin(z))

            return ra, dec

        def single_spherical_clip(poly1_vectors, poly2_vectors):
            """ single_spherical_clip """
            p1_ra, p1_dec = vectors_to_radec(poly1_vectors)
            p2_ra, p2_dec = vectors_to_radec(poly2_vectors)
            p1 = SingleSphericalPolygon.from_radec(p1_ra, p1_dec, degrees=True)
            p2 = SingleSphericalPolygon.from_radec(p2_ra, p2_dec, degrees=True)
            return p1.intersection(p2)

        def vector_to_radec(vector):
            """ vector_to_radec """
            x, y, z = vector
            ra  = np.degrees(np.arctan2(y, x)) % 360
            dec = np.degrees(np.arcsin(z))
            return ra, dec

        pixels = []
        radec_deg = []

        print('Earth.fov_intercept_earth(): fov_icrs=', fov_icrs.shape)
        print('Earth.fov_intercept_earth(): earth_disc_icrs=', earth_disc_icrs.shape)

        visible_polygon = single_spherical_clip(fov_icrs, earth_disc_icrs)

        if len(visible_polygon) == 0:
            print('Earth.fov_intercept_earth(): pixels=', pixels)
            return radec_deg

        for points in visible_polygon.points:
            print('Earth.fov_intercept_earth(): len(points)=', len(points))
            for point in points:
                ra_deg, dec_deg = vector_to_radec(point)
                radec_deg.append((ra_deg, dec_deg))
                continue
                #try:
                #    px, py = camera.radec_to_pixel(ra_deg, dec_deg, attitude, obs_time)
                #    print('%s [%5.1f,%5.1f] [%5d,%5d]' % (point, ra_deg, dec_deg, px, py))
                #except CameraIntrinsicsError as e:
                #    print('%s [%5.1f,%5.1f] %s' % (point, ra_deg, dec_deg, str(e)))
                #    continue
                #pixels.append((px, py))

        print('Earth.fov_intercept_earth(): radec_deg=', radec_deg)
        return radec_deg

        #print('Earth.fov_intercept_earth(): pixels=', pixels)
        #return pixels

    def _compute_earth_disc_polygon(self, sat_icrs:SkyCoord, obs_time:datetime, nsteps:int=200):
        """
        Compute the apparent Earth disc (limb) as seen from a satellite.

        Returns:
            Nx3 array of unit vectors in ICRS pointing to the Earth limb.
        """

        # Satellite position in ITRS (ECEF)
        sat_itrs = sat_icrs.transform_to(ITRS(obstime=obs_time))

        # Satellite distance from Earth's center (km)
        sat_pos = np.array([
            sat_itrs.x.to(u.km).value,
            sat_itrs.y.to(u.km).value,
            sat_itrs.z.to(u.km).value
        ])
        sat_dist = np.linalg.norm(sat_pos)

        # Angular radius of Earth as seen from satellite
        theta_E = np.arcsin(u.R_earth.to(u.km) / sat_dist)

        # Direction to Earth's center in ICRS
        earth_icrs = SkyCoord(0*u.deg, 0*u.deg, distance=1*u.AU,
                              frame='gcrs', obstime=obs_time).transform_to('icrs')
        # Actually get Earth center properly:
        earth_icrs = SkyCoord(0*u.deg, 0*u.deg, frame=GCRS(obstime=obs_time)).transform_to('icrs')

        # Vector from satellite to Earth center
        earth_vec = earth_icrs.cartesian.xyz.value - sat_icrs.cartesian.xyz.value
        earth_vec /= np.linalg.norm(earth_vec)

        # Build orthonormal basis around earth_vec
        # Pick an arbitrary vector not parallel to earth_vec
        tmp = np.array([0, 0, 1.0])
        if abs(np.dot(tmp, earth_vec)) > 0.9:
            tmp = np.array([0, 1.0, 0])

        # First perpendicular axis
        u_vec = np.cross(earth_vec, tmp)
        u_vec /= np.linalg.norm(u_vec)

        # Second perpendicular axis
        v_vec = np.cross(earth_vec, u_vec)

        # Generate limb points
        limb_vectors = []
        for phi in np.linspace(0, 2*np.pi, nsteps, endpoint=False):
            # Rotate earth_vec by theta_E around the circle
            limb = (earth_vec * np.cos(theta_E) +
                    u_vec * np.sin(theta_E) * np.cos(phi) +
                    v_vec * np.sin(theta_E) * np.sin(phi))
            limb_vectors.append(limb)

        return np.array(limb_vectors)
