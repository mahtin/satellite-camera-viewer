"""
SatelliteOrbit

Satellite orbit from 2LE or TLE/3LE
"""

# Earth-Centered Inertial (ECI) position and velocity define a satellite's state vector ([r,v]) using Cartesian
# coordinates (x,y,z) relative to the center of the Earth, which does not rotate with the planet, remaining fixed
# relative to stars. It provides an inertial, non-accelerating frame where Z points to the North Pole and the
# XY-plane is the equatorial plane.
#
# In an Earth-centered inertial (ECI) frame, the X-axis (often denoted as I) points towards the vernal equinox
# (or First Point of Aries). This direction is the intersection of the equatorial plane and the ecliptic plane,
# acting as a fixed reference point in space, not rotating with the Earth.
# Key characteristics of the ECI frame (X,Y,Z):
# Origin: The center of mass of the Earth.
# X-axis (I): Points to the vernal equinox (intersection of the equatorial plane and the ecliptic plane).
# Y-axis (J): Completes the right-hand system by being perpendicular to X and Z.
# Z-axis (K): Passes through the North Pole.
# Purpose: It is non-rotating, ideal for determining satellite orbits and celestial navigation.
# Note: The specific inertial reference frame used is often the J2000 frame, meaning the X-axis points to the
# vernal equinox at the epoch of Jan 1, 2000, at noon.

from datetime import datetime, timezone
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, TEME, GCRS, ITRS, EarthLocation, get_body
import astropy.units as u
from scipy.spatial.transform import Rotation as R

from sgp4.api import SGP4_ERRORS
from sgp4.conveniences import sat_epoch_datetime

class SatelliteOrbitError(Exception):
    """ SatelliteOrbitError """

class SatelliteOrbit:
    """ SatelliteOrbit """

    def __init__(self, tle:TLE=None):
        """
        SatelliteOrbit - accept a TLE/3LE or 2LE via TLE class.

        :param tle: TLEs.
        :type tle: TLE
        """
        self.tle = tle

    def __str__(self):
        return str(self.tle)

    @property
    def tle(self):
        """
        tle - return TLE class

        :return: TLE class
        :rtype: TLE
        """
        return self._tle

    @tle.setter
    def tle(self, tle=None):
        """
        tle - return TLE class

        :param tle: TLE class
        :type tle: TLE
        """
        if tle is None:
            raise SatelliteOrbitError('TLE must be provide') from None
        self._tle = tle

    @property
    def satellite(self):
        """ satellite """
        try:
            return self.tle.satrec
        except ValueError:
            raise SatelliteOrbitError('TLE has invalid format') from None
        except FileNotFoundError:
            raise SatelliteOrbitError('TLE not found') from None

    @property
    def sat_num(self):
        """ sat_num """
        return self.satellite.satnum

    def _teme(self, observed_time):
        """
        _teme() - TEME (True Equator, Mean Equinox) - an Earth-centered inertial (ECI) coordinate frame

        :param observed_time: Observed Time (in UTC).
        :type t: ObservedTime
        :return: r_teme_km, v_teme_km_s
        :rtype: tuple
        """
        # error: nonzero for any dates that produced errors, 0 otherwise.
        # r_teme_km: position vectors in kilometers.
        # v_teme_km_s: velocity vectors in kilometers per second.
        # The positional vectors returned by SGP4 are in TEME (True Equator Mean Equinox)
        t = observed_time.t
        error, r_teme_km, v_teme_km_s = self.satellite.sgp4(t.jd1, t.jd2)
        if error != 0:
            raise RuntimeError('SGP4 error value/code: %d: "%s"' % (error, SGP4_ERRORS[error])) from None
        # r_teme_km, v_teme_km_s are in True Equator, Mean Equinox (TEME); for many RA/Dec uses, direction is close enough,
        # but for rigor you'd convert TEME -> ECI (e.g., ITRF/GCRS).
        return r_teme_km, v_teme_km_s

    def _lvlh(self, observed_time):
        """
        _lvlh() - LVLH (Local Vertical, Local Horizontal) - a rotating, spacecraft-centered coordinate system

        :param observed_time: Observed Time (in UTC).
        :type observed_time: ObservedTime

        :return: Returns LVLH frame unit vectors from time (and hence ECI position and velocity).
            Based on ESA ISS Reference Frame Definition:
            Z_LVLH = -r_hat (nadir or -zenith)
            Y_LVLH = -h_hat (opposite orbit normal)
            X_LVLH = Y × Z (velocity direction)
        :rtype: dict
        """
        r_eci, v_eci = self._teme(observed_time)
        r = np.array(r_eci)
        v = np.array(v_eci)

        z_lvlh = -r / np.linalg.norm(r)
        h = np.cross(r, v)
        y_lvlh = -h / np.linalg.norm(h)
        x_lvlh = np.cross(y_lvlh, z_lvlh)

        return {'X': x_lvlh, 'Y': y_lvlh, 'Z': z_lvlh}

    def _sun_vector_eci_km(self, observed_time):
        """
        _sun_vector_eci_km() - Returns Sun vector in ECI (GCRS) coordinates, km.

        :param observed_time: Observed Time (in UTC).
        :type observed_time: ObservedTime

        """
        sun_gcrs = get_body('sun', observed_time.t)

        x = sun_gcrs.cartesian.x.to(u.km).value
        y = sun_gcrs.cartesian.y.to(u.km).value
        z = sun_gcrs.cartesian.z.to(u.km).value

        return np.array([x, y, z])

    def sat_in_eclipse(self, observed_time):
        """
        in_eclipse - Returns True if saetellite is in Earth's umbra (full shadow).

        :param observed_time: Observation time (in UTC).
        :type observed_time: ObservedTime
        :return: is satellite in eclipse
        :rtype: bool
        """

        sun_eci_km = self._sun_vector_eci_km(observed_time)
        # Unit vector from Earth to Sun
        sun_vec = sun_eci_km / np.linalg.norm(sun_eci_km)

        sat_eci_km = self.eci_position_vector(observed_time)
        # Projection of satellite position onto Sun direction
        projection_scalar = np.dot(sat_eci_km, sun_vec)

        # If satellite is on the sunward side of Earth → cannot be in shadow
        if projection_scalar > 0:
            return False

        # Perpendicular distance from satellite to Sun line
        perpendicular_distance = np.linalg.norm(sat_eci_km - projection_scalar * sun_vec)

        # is satellite inside Earth's shadow cylinder?
        return perpendicular_distance < u.R_earth.to(u.km)

    def sat_solar_beta_angle(self, observed_time):
        """
        sat_solar_beta_angle - return beta angle

        :param observed_time: Observation time (in UTC).
        :type observed_time: ObservedTime
        :return: beta angle in degrees
        :rtype: float

        In orbital mechanics, the beta angle (β) is the angle between a satellite's orbital plane around
        Earth and the geocentric position of the Sun. The beta angle determines the percentage of time
        that a satellite in low Earth orbit (LEO) spends in direct sunlight, absorbing solar radiation

        Yearly Variation: The satelite beta angle fluctuates during the year. For example, the ISS valies
        between roughly -75 and +75 degrees over a 60-day precession period and on an annual cycle.
        """
        r_eci, v_eci = self._teme(observed_time)

        sun_eci = self._sun_vector_eci_km(observed_time)
        s_hat = sun_eci / np.linalg.norm(sun_eci)
        h = np.cross(r_eci, v_eci)
        h_hat = h / np.linalg.norm(h)
        beta = np.arcsin(np.dot(h_hat, s_hat))
        return np.degrees(beta)

    def eci_position_vector(self, observed_time):
        """
        Returns ECI (Earth-Centered Inertial) position (km) at UTC time observed_time.
        """
        r_teme_km, _ = self._teme(observed_time)
        return np.array(r_teme_km)

    def eci_velocity_vector(self, observed_time):
        """
        Returns ECI (Earth-Centered Inertial) velocity (km/s) at UTC time observed_time.
        """
        _, v_teme_km_s = self._teme(observed_time)
        return np.array(v_teme_km_s)

    def icrs(self, observed_time):
        """ icrs - convert satellite and time into a ICRS value """
        # ICRS is International Celestial Reference System (ICRS)
        r_teme_km, _ = self._teme(observed_time)
        sat_icrs = SkyCoord(x=r_teme_km[0]*u.km, y=r_teme_km[1]*u.km, z=r_teme_km[2]*u.km, frame=TEME(obstime=observed_time.t)).transform_to('icrs')
        return sat_icrs

    def sat_lon_lat_alt(self, observed_time):
        """
        sat_lon_lat_alt - Return satellite geodetic lat, lon, alt.

        Parameters
        ----------
        observed_time : astropy Time
            Observation time.

        Returns
        -------
        lat_deg : float
        lon_deg : float
        alt_km : float
        """

        sat_eci_km = self.eci_position_vector(observed_time)

        # 1. Wrap ECI vector in a GCRS SkyCoord using CartesianRepresentation
        sat_gcrs = SkyCoord(x=sat_eci_km[0] * u.km, y=sat_eci_km[1] * u.km, z=sat_eci_km[2] * u.km, frame=GCRS(obstime=observed_time.t), representation_type='cartesian')

        # 2. Convert to Earth-fixed International Terrestrial Reference System (ITRS)
        sat_itrs = sat_gcrs.transform_to(ITRS(obstime=observed_time.t))

        # 3. Convert to geodetic lat/lon/alt
        sat_loc = EarthLocation.from_geocentric(sat_itrs.x, sat_itrs.y, sat_itrs.z)

        sat_lon_deg = sat_loc.lon.to_value(u.deg)
        sat_lat_deg = sat_loc.lat.to_value(u.deg)
        sat_alt_km = sat_loc.height.to_value(u.km)

        if sat_lon_deg < 0.0:
            sat_lon_deg += 360.0
        return sat_lon_deg, sat_lat_deg, sat_alt_km

    def sat_rev_per_day(self):
        """ sat_rev_per_day """
        mean_motion_per_min_rad = self.satellite.no
        # Convert to revolutions per day for easier reading
        rev_per_day = mean_motion_per_min_rad * 60.0 * 24.0 / (2.0 * np.pi)
        return rev_per_day

    def sat_period_seconds(self):
        """ sat_period_seconds """
        period_seconds = 60.0 * 60.0 * 24.0 / self.sat_rev_per_day()
        return period_seconds

    def sat_epoch_age(self):
        """ sat_epoch_age """
	# removing microseconds because this is just for display reasons only (not satellite orbit location)
        tle_epoch_utc = sat_epoch_datetime(self.satellite).replace(microsecond=0, tzinfo=timezone.utc)
        current_time_utc = datetime.now(timezone.utc).replace(microsecond=0)
        return current_time_utc - tle_epoch_utc

    def sat_altitude_inclination(self):
        """ sat_altitude - Perigee, Apogee, and Inclination """
        return self.satellite.radiusearthkm * self.satellite.altp, self.satellite.radiusearthkm * self.satellite.alta, self.satellite.inclo

    def sat_xvv_attitude_quaternion(self, observed_time):
        """
        sat_xvv_attitude_quaternion() - XVV ATTITUDE (X-axis aligned with velocity)

        Construct quaternion for XVV attitude:
          +X = velocity direction
          +Z = nadir
          +Y = completes RH frame
        """
        lvlh = self._lvlh(observed_time)
        R_body = np.vstack([lvlh['X'], lvlh['Y'], lvlh['Z']])
        return R.from_matrix(R_body).as_quat(scalar_first=True)

    # ------------------------------------------------------------
    # ISS Specific functions
    # ------------------------------------------------------------

    def iss_tea_offsets_deg(self, port_config='DEFAULT'):
        """
        iss_tea_offsets_deg() - TEA (Torque Equilibrium Attitude) OFFSETS (NASA MCS)
        TEA values from NASA ISS Motion Control System documentation:
        Current +XVV TEA: yaw=-4 deg, roll=0.9 deg
        Pitch varies from -12 to -2 deg depending on visiting vehicles.
        """
        if port_config == 'DEFAULT':
            pitch = -7.0    # midpoint of NASA's -12 to -2 deg range
        else:
            pitch = port_config

        tea_deg = {
            'yaw': -4.0,
            'pitch': pitch,
            'roll': 0.9,
        }
        return tea_deg

    def iss_apply_tea_to_quaternion(self, q, tea_deg):
        """
        iss_apply_tea_to_quaternion() - Apply TEA yaw/pitch/roll offsets to a base attitude quaternion.
        """
        r_base = R.from_quat(q, scalar_first=True)
        r_tea = R.from_euler('ZYX', [tea_deg['yaw'], tea_deg['pitch'], tea_deg['roll']], degrees=True)
        return (r_tea * r_base).as_quat(scalar_first=True)

    _iss_docking_port_axes_body = {
        # Body-frame unit vectors for ISS docking ports.
        # Based on ISS body axes defined in ESA reference frames.
        # https://www.nasa.gov/wp-content/uploads/2022/06/508318main_iss_ref_guide_nov2010.pdf
        # Unity (Node 1)
        # Harmony (Node 2)
        # Tranquility (Node 3 - except it's not really called Node 3)

        # PORT NAME         [X (Velocity Vector), Y (left, perpendicular to the orbital plane), Z (Zenith or -Nadir)]
        'N1_QUEST_AIRLOCK': np.array([ 0,-1, 0]),    # Unity (Node 1) Starboard (right)
        'N1_STARBOARD':     np.array([ 0,-1, 0]),
        'HARMONY_FORWARD':  np.array([+1, 0, 0]),    # Dragon/Starliner/Space Shuttle berthing
        'N2_FORWARD':       np.array([+1, 0, 0]),
        'HARMONY_ZENITH':   np.array([ 0, 0,+1]),    # Dragon/Starliner berthing
        'N2_ZENITH':        np.array([ 0, 0,+1]),
        'HARMONY_NADIR':    np.array([ 0, 0,-1]),    # Dragon/HTV/Cygnus berthing
        'N2_NADIR':         np.array([ 0, 0,-1]),
        'KIBO':             np.array([ 0,+1, 0]),    # Japanese Experiment Module (JAXA) (left)
        'N2_PORT':          np.array([ 0,+1, 0]),
        'COLUMBUS':         np.array([ 0,-1, 0]),    # The Columbus Laboratory Module (ESA) (right)
        'N2_STARBOARD':     np.array([ 0,-1, 0]),
        'CUPOLA':           np.array([ 0, 0,-1]),    # Tranquility (Node 3) Nadir port
        'N3_NADIR':         np.array([ 0, 0,-1]),
    }

    def iss_docking_ports(self):
        """ iss_docking_ports """
        return self._iss_docking_port_axes_body.keys()

    def iss_docking_port_vector_eci(self, port_name, quaternion_wxyz):
        """
        docking_port_vector_eci() - DOCKING PORT GEOMETRY (Derived from ISS body axes)
        Body-frame unit vectors for ISS docking ports.
        Based on ISS body axes defined in ESA reference frames.

        Parameters:
            port_name  : ISS port name
        """
        try:
            iss_body_vec = self._iss_docking_port_axes_body[port_name]
        except KeyError:
            raise ValueError('Unknown ISS port: %s' % (port_name)) from None
        r = R.from_quat(quaternion_wxyz, scalar_first=True)
        return r.apply(iss_body_vec)
