""" SatelliteCamera """

from datetime import datetime, timedelta, timezone

from .BrownConradyCoeffs import BrownConradyCoeffs as cBCC
from .CameraIntrinsics import CameraIntrinsics as cCI, CameraIntrinsicsError
from .CameraAttitude import CameraAttitude as cCA
from .CameraAttitude import Attitude as cA
from .CameraAttitude import Quaternion as cQ
from .CameraFOV import CameraFOV as cCF
from .SatelliteOrbit import SatelliteOrbit as cSO
from .Earth import Earth as cE, EarthError

class SatelliteCameraError(Exception):
    """ SatelliteCameraError """

class SatelliteCamera():
    """ SatelliteCamera """

    # All the classes...
    BrownConradyCoeffs = cBCC
    CameraIntrinsics = cCI
    CameraAttitude = cCA
    Attitude = cA
    Quaternion = cQ
    CameraFOV = cCF
    SatelliteOrbit = cSO
    Earth = cE

    # Based on the Raspberry Pi High Quality (HQ) camera
    # 12.3-megapixel Sony IMX477
    # https://www.sony-semicon.com/files/62/pdf/p-13_IMX477-AACK_Flyer.pdf
    def __init__(self,
            focal_length_mm: float = 12.0,         # focal length (mm)
            sensor_size_x_mm: float = 6.287,       # sensor width (mm)
            sensor_size_y_mm: float = 4.712,       # sensor height (mm)
            nx: int = 4056,                        # pixels in x
            ny: int = 3040,                        # pixels in y
            cx: float = None,                      # principal point x (pixels)
            cy: float = None,                      # principal point y (pixels)
            bcc: BrownConradyCoeffs = None,        # Brown Conrady Coeffs
            sensor_to_lens_mm: float = None        # distance from sensor to lens principal plane
        ):
        """ SatelliteCamera """
        self._focal_length_mm = focal_length_mm
        self._sensor_size = [sensor_size_x_mm, sensor_size_y_mm]
        self._n = [nx, ny]
        self._c = [cx, cy]
        self._bcc = bcc
        if sensor_to_lens_mm is None:
            self._sensor_to_lens_mm = self._focal_length_mm
        else:
            self._sensor_to_lens_mm = sensor_to_lens_mm
        self._rebuild_camera()
        self._obs_time = None
        self.now()
        self._sat_orbit = None
        self._sat_quat_body_to_eci = None
        self._sat_attitude = None
        self._cam_attitude = None
        self._reset_attitude()

    def reload(self,
            focal_length_mm: float = None,         # focal length (mm)
            sensor_size_x_mm: float = None,        # sensor width (mm)
            sensor_size_y_mm: float = None,        # sensor height (mm)
            nx: int = None,                        # pixels in x
            ny: int = None,                        # pixels in y
            cx: float = None,                      # principal point x (pixels)
            cy: float = None,                      # principal point y (pixels)
            bcc: BrownConradyCoeffs = None,        # Brown Conrady Coeffs
            sensor_to_lens_mm: float = None        # distance from sensor to lens principal plane
        ):
        """ reload """
        if focal_length_mm is not None:
            self._focal_length_mm = focal_length_mm
        if sensor_size_x_mm is not None:
            self._sensor_size[0] = sensor_size_x_mm
        if sensor_size_y_mm is not None:
            self._sensor_size[1] = sensor_size_y_mm
        if nx is not None:
            self._n[0] = nx
        if ny is not None:
            self._n[1] = ny
        if cx is not None:
            self._c[0] = cx
        if cy is not None:
            self._c[1] = cy
        if bcc is not None:
            self._bcc = bcc
        if sensor_to_lens_mm is None:
            self._sensor_to_lens_mm = self._focal_length_mm
        else:
            self._sensor_to_lens_mm = sensor_to_lens_mm
        self._rebuild_camera()

    def _rebuild_camera(self):
        """ _rebuild_camera """
        self._camera = self.CameraIntrinsics(
            focal_length_mm=self._focal_length_mm,
            sensor_size_x_mm=self._sensor_size[0], sensor_size_y_mm=self._sensor_size[1],
            nx=self._n[0], ny=self._n[1],
            cx=self._c[0], cy=self._c[1],
            bcc=self._bcc,
            sensor_to_lens_mm=self._sensor_to_lens_mm
        )

    def _rebuild_sat_orbit(self):
        """ _rebuild_sat_orbit """
        if self._sat_orbit is None:
            self._sat_orbit = self.SatelliteOrbit(tle=self._tle)
        else:
            self._sat_orbit.tle = self._tle
        self._earth = self.Earth(self.sat_orbit)

    def _rebuild_attitude(self):
        """ _rebuild_attitude """

        if self._attitude is not None:
            return
        if self._sat_quat_body_to_eci is not None:
            self._attitude = self.CameraAttitude(sat_quat_body_to_eci=self._sat_quat_body_to_eci, cam_attitude=self.cam_attitude)
        elif self.sat_attitude is not None and self.cam_attitude is not None:
            self._attitude = self.CameraAttitude(sat_attitude=self.sat_attitude, cam_attitude=self.cam_attitude)
        else:
            # hopefully this will be recaculated again
            pass

    def _reset_attitude(self):
        """ _reset_attitude """
        self._attitude = None

    @property
    def attitude(self):
        """ attitude """
        self._rebuild_attitude()
        return self._attitude

    @attitude.setter
    def attitude(self, value=None):
        """ attitude """
        self._attitude = value
        self._rebuild_attitude()

    def __str__(self) -> str:
        return str(self._camera)

    def datetime(self, year, month, day, hour, minute, second):
        """ Observation time - fixed """
        self._obs_time = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)

    def now(self):
        """ Observation time - updating to time now """
        self._obs_time = datetime.now(timezone.utc)

    def adjust_by_seconds(self, delta: int):
        """ accelerate time """
        self._obs_time += timedelta(seconds=delta)

    @property
    def obs_time(self):
        """ obs_time """
        return self._obs_time

    @obs_time.setter
    def obs_time(self, value=None):
        """ obs_time """
        self._obs_time = value

    @property
    def camera(self):
        """ camera """
        return self._camera

    @property
    def focal_length_mm(self):
        """ focal_length_mm """
        return self._focal_length_mm

    @focal_length_mm.setter
    def focal_length_mm(self, value=None):
        """ focal_length_mm """
        if value is None:
            raise ValueError('focal_length_mm cannot be empty') from None
        self._focal_length_mm = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def sensor_size_x_mm(self):
        """ sensor_size_x_mm """
        return self._sensor_size[0]

    @sensor_size_x_mm.setter
    def sensor_size_x_mm(self, value=None):
        """ sensor_size_x_mm """
        if value is None:
            raise ValueError('sensor_size_x_mm cannot be empty') from None
        self._sensor_size[0] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def sensor_size_y_mm(self):
        """ sensor_size_y_mm """
        return self._sensor_size[1]

    @sensor_size_y_mm.setter
    def sensor_size_y_mm(self, value=None):
        """ sensor_size_y_mm """
        if value is None:
            raise ValueError('sensor_size_y_mm cannot be empty') from None
        self._sensor_size[1] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def nx(self):
        """ nx """
        return self._n[0]

    @nx.setter
    def nx(self, value=None):
        """ nx """
        if value is None:
            raise ValueError('nx cannot be empty') from None
        self._n[0] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def ny(self):
        """ ny """
        return self._n[1]

    @ny.setter
    def ny(self, value=None):
        """ ny """
        if value is None:
            raise ValueError('ny cannot be empty') from None
        self._n[1] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def cx(self):
        """ cx """
        return self._c[0]

    @cx.setter
    def cx(self, value=None):
        """ cx """
        if value is None:
            raise ValueError('cx cannot be empty') from None
        self._c[0] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def cy(self):
        """ cy """
        return self._c[1]

    @cy.setter
    def cy(self, value=None):
        """ cy """
        if value is None:
            raise ValueError('cy cannot be empty') from None
        self._c[1] = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def bcc(self):
        """ bcc """
        return self._bcc

    @bcc.setter
    def bcc(self, value=None):
        """ bcc """
        if value is None:
            raise ValueError('bcc cannot be empty') from None
        self._bcc = value
        # rebuild camera
        self._rebuild_camera()

    @property
    def tle(self):
        """ tle """
        return self._tle

    @tle.setter
    def tle(self, value=None):
        """ tle """
        self._tle = value
        self._rebuild_sat_orbit()

    @property
    def sat_orbit(self):
        """ sat_orbit """
        return self._sat_orbit

    @property
    def sat_quat_body_to_eci(self):
        """ sat_quat_body_to_eci """
        return self._sat_quat_body_to_eci

    @sat_quat_body_to_eci.setter
    def sat_quat_body_to_eci(self, value=None):
        """ sat_quat_body_to_eci """
        self._sat_quat_body_to_eci = value
        self._sat_attitude = None
        self._reset_attitude()

    @property
    def sat_attitude(self):
        """ sat_attitude """
        return self._sat_attitude

    @sat_attitude.setter
    def sat_attitude(self, value=None):
        """ sat_attitude """
        self._sat_attitude = value
        self._sat_quat_body_to_eci = None
        self._reset_attitude()

    @property
    def cam_attitude(self):
        """ cam_attitude """
        return self._cam_attitude

    @cam_attitude.setter
    def cam_attitude(self, value=None):
        """ cam_attitude """
        self._cam_attitude = value
        self._reset_attitude()

    def choose_attitude(self, pointing:str=None,
        sat_yaw_deg=None, sat_pitch_deg=None, sat_roll_deg=None,
        cam_yaw_deg=None, cam_pitch_deg=None, cam_roll_deg=None,
        qw=None, qx=None, qy=None, qz=None,
        earth_lat_deg=None, earth_lon_deg=None,
        star_ra_deg=None, star_dec_deg=None
    ):
        """ choose_attitude """

        # Inertial Pointing:
        #  A non-tumbling satellite keeps its antennas or cameras pointed at the same spot in space (inertial space).
        #  As it follows the curve of the Earth, its "down" side will gradually point towards the side, then up, then
        #  towards the other side over one orbit.
        # Earth-Pointing Need:
        #  To keep one side constantly aimed at the Earth (nadir pointing), a satellite must actively rotate at the
        #  same rate it orbits (once per orbit). I.e. Reaction Wheels / Momentum Wheels, Control Moment Gyros (CMGs),
        #  Thrusters (Propulsion), or Magnetorquers (Magnetic Torquers)

        verbose = False
        if verbose:
            print('choose_attitude()',
                'pointing=', pointing,
                'sat=', sat_yaw_deg, sat_pitch_deg, sat_roll_deg,
                'cam=', cam_yaw_deg, cam_pitch_deg, cam_roll_deg,
                'q[wxyz]=', qw, qx, qy, qz,
                'earth=', earth_lat_deg, earth_lon_deg,
                'star=', star_ra_deg, star_dec_deg
            )

        # we always reset and recaculate later
        self._reset_attitude()

        # Satellite pointing - if defined
        if None not in [sat_yaw_deg, sat_pitch_deg, sat_roll_deg]:
            if verbose:
                print('choose_attitude(): set sat')
            self._sat_attitude = self.Attitude(sat_yaw_deg, sat_pitch_deg, sat_roll_deg)
            self._sat_quat_body_to_eci = None
            if verbose:
                print('choose_attitude(): set sat', self.sat_attitude)
        else:
            self._sat_attitude = None
            self._sat_quat_body_to_eci = None
            if verbose:
                print('choose_attitude(): set sat', 'None')

        # Camera pointing - if defined
        if None not in [cam_yaw_deg, cam_pitch_deg, cam_roll_deg]:
            self._cam_attitude = self.Attitude(cam_yaw_deg, cam_pitch_deg, cam_roll_deg)
            if verbose:
                print('choose_attitude(): set cam', self.cam_attitude)
        else:
            self._cam_attitude = None
            if verbose:
                print('choose_attitude(): set cam', 'None')

        # Example: Satellite pointing arbitrary direction (y/p/r) + camera offset (y/p/r) defined above (hopefully)
        if pointing == 'arbitrary':
            return

        # Quaternion pointing - if defined, just do it (even with camera y/p/r defined above)
        if pointing == 'quaternion':
            if None in [qw, qx, qy, qz]:
                raise ValueError('%s: invalid pointing value' % (pointing)) from None
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_wxyz(qw, qx, qy, qz)
            return

        # Velocity-vector pointing camera (even with camera y/p/r defined above)
        if pointing == 'vv':
            r_teme_km = self.eci_position_vector()
            v_teme_km_s = self.eci_velocity_vector()
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.obs_time)
            v_gcrs_km_s = self.CameraAttitude.teme_to_gcrs_vector(v_teme_km_s, self.obs_time)  # same converter works
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_velocity_pointing(r_gcrs_km, v_gcrs_km_s)
            return

        # Nadir-pointing camera (even with camera y/p/r defined above)
        if pointing == 'nadir':
            r_teme_km = self.eci_position_vector()
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.obs_time)
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_nadir_pointing(r_gcrs_km)
            return

        # Point camera at ground location (lat,lon) - if defined, just do it (even with camera y/p/r defined above)
        if pointing == 'ground':
            if None in [earth_lat_deg, earth_lon_deg]:
                raise ValueError('%s: invalid pointing value' % (pointing)) from None
            # Point camera at ground location (lat,lon)
            r_teme_km = self.eci_position_vector()
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.obs_time)
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_pointing_ground(lat_deg=earth_lat_deg, lon_deg=earth_lon_deg, obs_time=self.obs_time, r_sat_gcrs_km=r_gcrs_km)
            return

        # Point camera at star (ra,dec) - if defined, just do it (even with camera y/p/r defined above)
        if pointing == 'star':
            if None in [star_ra_deg, star_dec_deg]:
                raise ValueError('%s: invalid pointing value' % (pointing)) from None
            # Point camera at ra/dec
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_pointing_radec(ra_deg=star_ra_deg, dec_deg=star_dec_deg, obs_time=self.obs_time)
            return

        # Default null quaternion (even with camera y/p/r defined above)
        if pointing == 'undefined':
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_wxyz()
            return

        raise ValueError('%s: invalid pointing value' % (pointing)) from None

    def eci_position_vector(self):
        """ eci_position_vector """
        return self.sat_orbit.eci_position_vector(self.obs_time)

    def eci_velocity_vector(self):
        """ eci_velocity_vector """
        if self.sat_orbit is None:
            return None
        return self.sat_orbit.eci_velocity_vector(self.obs_time)

    def sat_lon_lat_alt(self):
        """ sat_lon_lat_alt """
        return self.sat_orbit.sat_lon_lat_alt(self.obs_time)

    def pixel_to_radec(self, px, py):
        """ pixel_to_radec """
        return self.camera.pixel_to_radec(px, py, self.attitude, self.obs_time)

    def sensor_to_radec(self, nsteps):
        """ sensor_to_radec """
        return self.camera.sensor_to_radec(self.attitude, self.obs_time, nsteps=nsteps)

    def pixel_to_radec_and_vector(self, px, py):
        """ pixel_to_radec_and_vector """
        return self.camera.pixel_to_radec_and_vector(px, py, self.attitude, self.obs_time, sat_orbit=self.sat_orbit)

    def radec_to_pixel(self, ra_deg, dec_deg):
        """ radec_to_pixel """
        try:
            return self.camera.radec_to_pixel(ra_deg, dec_deg, self.attitude, self.obs_time)
        except CameraIntrinsicsError as e:
            raise SatelliteCameraError(str(e)) from None

    def camera_fov_radec_box(self):
        """ camera_fov_radec_box """
        return self.CameraFOV.camera_fov_radec_box(self.camera, self.attitude, self.obs_time)

    def camera_fov_solid_angle(self):
        """ camera_fov_solid_angle """
        return self.CameraFOV.camera_fov_solid_angle(self.camera, self.attitude, self.obs_time)

    def camera_fov_angular_width_height(self):
        """ camera_fov_angular_width_height """
        return self.CameraFOV.camera_fov_angular_width_height(self.camera, self.attitude, self.obs_time)

    def camera_fov_convex_hull(self, border_step:int):
        """ camera_fov_convex_hull """
        return self.CameraFOV.camera_fov_convex_hull(self.camera, self.attitude, self.obs_time, border_step=border_step)

    def camera_fov_border_vectors(self, border_step:int):
        """ camera_fov_border_vectors """
        return self.CameraFOV.camera_fov_border_vectors(self.camera, self.attitude, self.obs_time, border_step=border_step)

    def camera_fov_healpix_mask(self, nside:int):
        """ camera_fov_healpix_mask """
        return self.CameraFOV.camera_fov_healpix_mask(self.camera, self.attitude, self.obs_time, nside=nside)

    def earth_center_vector(self):
        """ earth_center_vector """
        return self._earth.earth_center_vector(self.obs_time)

    def earth_center_vector_icrs(self):
        """ earth_center_vector_icrs """
        return self._earth.earth_center_vector_icrs(self.obs_time)

    def earth_center_radec_simple(self):
        """ earth_center_radec_simple """
        return self._earth.earth_center_radec_simple(self.obs_time)

    def earth_center_radec(self):
        """ earth_center_radec """
        return self._earth.earth_center_radec(self.attitude, self.obs_time)

    def earth_angular_radius(self):
        """ earth_angular_radius """
        return self._earth.earth_angular_radius(self.obs_time)

    def camera_fov_intercept_earth(self, border_step:int=None):
        """ camera_fov_intercept_earth """
        try:
            return self._earth.camera_fov_intercept_earth(self.camera, self.attitude, self.obs_time, border_step=border_step)

        except EarthError as e:
            raise SatelliteCameraError(str(e)) from None
