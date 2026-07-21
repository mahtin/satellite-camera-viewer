""" SatelliteCamera """

from datetime import datetime, timezone

from .BrownConradyCoeffs import BrownConradyCoeffs as cBCC
from .CameraIntrinsics import CameraIntrinsics as cCI, CameraIntrinsicsError
from .CameraAttitude import CameraAttitude as cCA, Attitude as cA, Quaternion as cQ
from .CameraSensors import CameraSensor as cS, CameraSensors as cSs
from .CameraFOV import CameraFOV as cCF
from .SatelliteOrbit import SatelliteOrbit as cSO
from .Earth import Earth as cE, EarthError
from .ObservedTime import ObservedTime as oT

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
    CameraSensor = cS
    CameraSensors = cSs
    CameraFOV = cCF
    SatelliteOrbit = cSO
    Earth = cE
    ObservedTime = oT

    def __init__(self, camera_name:str=None, focal_length_mm:float=None):
        """ SatelliteCamera """

        if camera_name is None:
            # nasty hack to make default camera the first one defined ('cause Python dict()'s work this way)
            camera_name = next(iter(self.CameraSensors))
        try:
            self.camera_sensor = self.CameraSensors[camera_name]
        except IndexError:
            raise ValueError('%s: not found' % (camera_name))

        self._camera = self.CameraIntrinsics(self.camera_sensor, focal_length_mm=focal_length_mm)

        self._sensor_size = [self.camera_sensor.sensor_size_x_mm, self.camera_sensor.sensor_size_y_mm]
        self._n = [self.camera_sensor.nx, self.camera_sensor.ny]
        self._c = [self.camera_sensor.cx, self.camera_sensor.cy]
        self._bcc = self.camera_sensor.bcc
        if self.camera_sensor.sensor_to_lens_mm is None:
            self._sensor_to_lens_mm = self.camera_sensor.focal_length_mm
        else:
            self._sensor_to_lens_mm = self.camera_sensor.sensor_to_lens_mm
        self._sat_orbit = None
        self._sat_quat_body_to_eci = None
        self._sat_attitude = None
        self._cam_attitude = None
        self._reset_attitude()

        # seems like a legit value
        self.now()

    def reload(self, camera_name:str=None, focal_length_mm:float=None):
        """ reload """
        if camera_name is not None:
            try:
                self.camera_sensor = self.CameraSensors[camera_name]
            except IndexError:
                raise ValueError('%s: not found' % (camera_name))
            self._camera = self.CameraIntrinsics(self.camera_sensor, focal_length_mm=focal_length_mm)
            return
        if focal_length_mm is None:
            raise ValueError('focal_length_mm cannot be empty') from None
        self.camera_sensor.focal_length_mm = float(focal_length_mm)

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
        return str(self.camera)

    def now(self):
        """ Observation time - updating to time now """
        self.observed_time = self.ObservedTime()                # defaults to 'now'

    def adjust_by_seconds(self, delta: int):
        """ accelerate time """
        self.observed_time.timedelta(seconds=delta)

    @property
    def observed_time(self):
        """ observed_time """
        return self._observed_time

    @observed_time.setter
    def observed_time(self, value=None):
        """ observed_time """
        self._observed_time = value

    @property
    def camera(self):
        """ camera """
        return self._camera

    @property
    def focal_length_mm(self):
        """ focal_length_mm """
        return self.camera_sensor.focal_length_mm

    @focal_length_mm.setter
    def focal_length_mm(self, value=None):
        """ focal_length_mm """
        if value is None:
            raise ValueError('focal_length_mm cannot be empty') from None
        self.camera_sensor.focal_length_mm = float(value)

    @property
    def sensor_size_x_mm(self):
        """ sensor_size_x_mm """
        return self.camera_sensor.sensor_size_x_mm

    @property
    def sensor_size_y_mm(self):
        """ sensor_size_y_mm """
        return self.camera_sensor.sensor_size_y_mm

    @property
    def nx(self):
        """ nx """
        return self.camera_sensor.nx

    @property
    def ny(self):
        """ ny """
        return self.camera_sensor.ny

    @property
    def cx(self):
        """ cx """
        return self.camera_sensor.cx

    @property
    def cy(self):
        """ cy """
        return self.camera_sensor.cy

    @property
    def bcc(self):
        """ bcc """
        return self.camera_sensor.bcc

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
        #  As it follows the curve of the Earth, its 'down' side will gradually point towards the side, then up, then
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
            r_teme_km = self.eci_position_vector
            v_teme_km_s = self.eci_velocity_vector
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.observed_time)
            v_gcrs_km_s = self.CameraAttitude.teme_to_gcrs_vector(v_teme_km_s, self.observed_time)  # same converter works
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_velocity_pointing(r_gcrs_km, v_gcrs_km_s)
            return

        # Nadir-pointing camera (even with camera y/p/r defined above)
        if pointing == 'nadir':
            r_teme_km = self.eci_position_vector
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.observed_time)
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_nadir_pointing(r_gcrs_km)
            return

        # Point camera at ground location (lat,lon) - if defined, just do it (even with camera y/p/r defined above)
        if pointing == 'ground':
            if None in [earth_lat_deg, earth_lon_deg]:
                raise ValueError('%s: invalid pointing value' % (pointing)) from None
            # Point camera at ground location (lat,lon)
            r_teme_km = self.eci_position_vector
            r_gcrs_km = self.CameraAttitude.teme_to_gcrs_vector(r_teme_km, self.observed_time)
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_pointing_ground(lat_deg=earth_lat_deg, lon_deg=earth_lon_deg, observed_time=self.observed_time, r_sat_gcrs_km=r_gcrs_km)
            return

        # Point camera at star (ra,dec) - if defined, just do it (even with camera y/p/r defined above)
        if pointing == 'star':
            if None in [star_ra_deg, star_dec_deg]:
                raise ValueError('%s: invalid pointing value' % (pointing)) from None
            # Point camera at ra/dec
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_pointing_radec(ra_deg=star_ra_deg, dec_deg=star_dec_deg, observed_time=self.observed_time)
            return

        # Default null quaternion (even with camera y/p/r defined above)
        if pointing == 'undefined':
            self._sat_attitude = None
            self.sat_quat_body_to_eci = self.CameraAttitude.quaternion_wxyz()
            return

        raise ValueError('%s: invalid pointing value' % (pointing)) from None

    @property
    def eci_position_vector(self):
        """ eci_position_vector """
        return self.sat_orbit.eci_position_vector(self.observed_time)

    @property
    def eci_velocity_vector(self):
        """ eci_velocity_vector """
        if self.sat_orbit is None:
            return None
        return self.sat_orbit.eci_velocity_vector(self.observed_time)

    def sat_lon_lat_alt(self):
        """ sat_lon_lat_alt """
        return self.sat_orbit.sat_lon_lat_alt(self.observed_time)

    def sat_solar_beta_angle(self):
        """ sat_solar_beta_angle """
        return self.sat_orbit.sat_solar_beta_angle(self.observed_time)

    def sat_in_eclipse(self):
        """ sat_in_eclipse """
        return self.sat_orbit.sat_in_eclipse(self.observed_time)

    def sat_xvv_attitude_quaternion(self):
        """ sat_xvv_attitude_quaternion """
        return self.sat_orbit.sat_xvv_attitude_quaternion(self.observed_time)

    def iss_tea_offsets_deg(self, port_config='DEFAULT'):
        """ iss_tea_offsets_deg """
        return self.sat_orbit.iss_tea_offsets_deg(port_config)

    def iss_apply_tea_to_quaternion(self, q, tea_deg):
        """ iss_apply_tea_to_quaternion """
        return self.sat_orbit.iss_apply_tea_to_quaternion(q, tea_deg)

    def iss_docking_ports(self):
        """ iss_docking_ports """
        return self.sat_orbit.iss_docking_ports()

    def iss_docking_port_vector_eci(self, port_name, quaternion_wxyz):
        """ iss_docking_port_vector_eci """
        return self.sat_orbit.iss_docking_port_vector_eci(port_name, quaternion_wxyz)

    def pixel_to_radec(self, px, py):
        """ pixel_to_radec """
        return self.camera.pixel_to_radec(px, py, self.attitude, self.observed_time)

    def sensor_to_radec(self, nsteps):
        """ sensor_to_radec """
        return self.camera.sensor_to_radec(self.attitude, self.observed_time, nsteps=nsteps)

    def pixel_to_radec_and_vector(self, px, py):
        """ pixel_to_radec_and_vector """
        return self.camera.pixel_to_radec_and_vector(px, py, self.attitude, self.observed_time, sat_orbit=self.sat_orbit)

    def radec_to_pixel(self, ra_deg, dec_deg):
        """ radec_to_pixel """
        try:
            return self.camera.radec_to_pixel(ra_deg, dec_deg, self.attitude, self.observed_time)
        except CameraIntrinsicsError as e:
            raise SatelliteCameraError(str(e)) from None

    def camera_fov_radec_box(self):
        """ camera_fov_radec_box """
        return self.CameraFOV.camera_fov_radec_box(self.camera, self.attitude, self.observed_time)

    def camera_fov_solid_angle(self):
        """ camera_fov_solid_angle """
        return self.CameraFOV.camera_fov_solid_angle(self.camera, self.attitude, self.observed_time)

    def camera_fov_angular_width_height(self):
        """ camera_fov_angular_width_height """
        return self.CameraFOV.camera_fov_angular_width_height(self.camera, self.attitude, self.observed_time)

    def camera_fov_convex_hull(self, border_step:int):
        """ camera_fov_convex_hull """
        return self.CameraFOV.camera_fov_convex_hull(self.camera, self.attitude, self.observed_time, border_step=border_step)

    def camera_fov_border_vectors(self, border_step:int):
        """ camera_fov_border_vectors """
        return self.CameraFOV.camera_fov_border_vectors(self.camera, self.attitude, self.observed_time, border_step=border_step)

    def camera_fov_healpix_mask(self, nside:int):
        """ camera_fov_healpix_mask """
        return self.CameraFOV.camera_fov_healpix_mask(self.camera, self.attitude, self.observed_time, nside=nside)

    def earth_center_vector(self):
        """ earth_center_vector """
        return self._earth.earth_center_vector(self.observed_time)

    def earth_center_vector_icrs(self):
        """ earth_center_vector_icrs """
        return self._earth.earth_center_vector_icrs(self.observed_time)

    def earth_center_radec_simple(self):
        """ earth_center_radec_simple """
        return self._earth.earth_center_radec_simple(self.observed_time)

    def earth_center_radec(self):
        """ earth_center_radec """
        return self._earth.earth_center_radec(self.attitude, self.observed_time)

    def earth_angular_radius(self):
        """ earth_angular_radius """
        return self._earth.earth_angular_radius(self.observed_time)

    def camera_fov_intercept_earth(self, border_step:int=None):
        """ camera_fov_intercept_earth """
        try:
            return self._earth.camera_fov_intercept_earth(self.camera, self.attitude, self.observed_time, border_step=border_step)

        except EarthError as e:
            raise SatelliteCameraError(str(e)) from None
