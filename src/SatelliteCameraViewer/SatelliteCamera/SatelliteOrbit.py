"""
SatelliteOrbit

Satellite orbit from TLE
"""

from datetime import datetime, timezone
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, TEME, GCRS, ITRS, EarthLocation
import astropy.units as u

from sgp4.api import Satrec, WGS72, SGP4_ERRORS

class SatelliteOrbit:
    """ SatelliteOrbit """

    def __init__(self, tle:list=None):
        """
        SatelliteOrbit - accept a TLE or 3LE
        TLE or two-line element sets (no satellite name on Line 0).
        3LE or three-line element sets including 24-character satellite name on Line 0.

        :param tle: TLEs as an array (2 or 3 lines long).
        :type tle: list[str]
        """
        self.tle = tle

    def __str__(self):
        if len(self._tle) == 2:
            v = '["%s", "%s"]' % (self._tle[0], self._tle[1])
        else:
            v = '["%s", "%s", "%s"]' % (self._tle[0], self._tle[1], self._tle[2])
        return v

    @property
    def tle(self):
        """
        tle - return array of TLE strings (2 or 3 lines long)

        :return: TLEs
        :rtype: list[str]
        """
        return self._tle

    @tle.setter
    def tle(self, tle=None):
        """
        tle - return array of TLE strings (2 or 3 lines long).

        :param tle: TLEs as an array (2 or 3 lines long).
        :type tle: list[str]
        """
        self._tle = tle
        self._rebuild_from_tle()

    def _rebuild_from_tle(self):
        """ _rebuild_from_tle """
        if self._tle is None or len(self._tle) not in [2,3] or None in self._tle:
            self._sat = None
            raise ValueError('TLEs must provide satellite info as two or three lines of text') from None
        try:
            if len(self._tle) == 2:
                self._sat = Satrec.twoline2rv(self._tle[0], self._tle[1], WGS72)
            else:
                self._sat = Satrec.twoline2rv(self._tle[1], self._tle[2], WGS72)
        except ValueError:
            self._sat = None
            raise ValueError('TLEs have invalid format') from None

    def t(self, obs_time: datetime):
        """
        t - convert to Julian date and fractional Julian date

        :param obs_time: date and time in datetime form with UTC timezone
        :type obs_time: datetime
        :return: time in Jualian date form
        :rtype: Time

        """
        # Convert datetime -> Julian date and fractional Julian date
        return Time(obs_time.replace(tzinfo=timezone.utc))

    def _teme(self, t):
        """
        _teme

        :param t: Time in Juian date format
        :type t: Time
        :return: r_teme_km, v_teme_km_s
        :rtype: tuple
        """
        # e: nonzero for any dates that produced errors, 0 otherwise.
        # r: position vectors in kilometers.
        # v: velocity vectors in kilometers per second.
        e, r_teme_km, v_teme_km_s = self._sat.sgp4(t.jd1, t.jd2)
        if e != 0:
            raise RuntimeError('SGP4 error value/code: %d: "%s"' % (e, SGP4_ERRORS[e])) from None
        # r_teme_km, v_teme_km_s are in True Equator, Mean Equinox (TEME); for many RA/Dec uses, direction is close enough,
        # but for rigor you'd convert TEME -> ECI (e.g., ITRF/GCRS).
        return r_teme_km, v_teme_km_s

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

    def eci_position_vector(self, obs_time: datetime):
        """
        Returns ECI (Earth-Centered Inertial) position (km) at UTC time obs_time.
        """
        t = self.t(obs_time)
        r_teme_km, v_teme_km_s = self._teme(t)
        return np.array(r_teme_km)

    def eci_velocity_vector(self, obs_time: datetime):
        """
        Returns ECI (Earth-Centered Inertial) velocity (km/s) at UTC time obs_time.
        """
        t = self.t(obs_time)
        r_teme_km, v_teme_km_s = self._teme(t)
        return np.array(v_teme_km_s)

    def icrs(self, obs_time: datetime):
        """ icrs - convert satellite and time into a ICRS value """
        # ICRS is International Celestial Reference System (ICRS)
        t = self.t(obs_time)
        r_teme_km, v_teme_km_s = self._teme(t)
        sat_icrs = SkyCoord(x=r_teme_km[0]*u.km, y=r_teme_km[1]*u.km, z=r_teme_km[2]*u.km, frame=TEME(obstime=obs_time)).transform_to("icrs")
        return sat_icrs

    def lon_lat_alt(self, obs_time):
        """
        Return satellite geodetic lat, lon, alt.

        Parameters
        ----------
        obs_time : astropy Time
            Observation time.

        Returns
        -------
        lat_deg : float
        lon_deg : float
        alt_km : float
        """

        sat_eci_km = self.eci_position_vector(obs_time)

        # 1. Wrap ECI vector in a GCRS SkyCoord using CartesianRepresentation
        sat_gcrs = SkyCoord(
            x=sat_eci_km[0] * u.km,
            y=sat_eci_km[1] * u.km,
            z=sat_eci_km[2] * u.km,
            frame=GCRS(obstime=obs_time),
            representation_type='cartesian'
        )

        # 2. Convert to Earth-fixed International Terrestrial Reference System (ITRS)
        sat_itrs = sat_gcrs.transform_to(ITRS(obstime=obs_time))

        # 3. Convert to geodetic lat/lon/alt
        sat_loc = EarthLocation.from_geocentric(sat_itrs.x, sat_itrs.y, sat_itrs.z)

        sat_lon_deg = sat_loc.lon.to_value(u.deg)
        sat_lat_deg = sat_loc.lat.to_value(u.deg)
        sat_alt_km = sat_loc.height.to_value(u.km)

        if sat_lon_deg < 0.0:
            sat_lon_deg += 360.0
        return sat_lon_deg, sat_lat_deg, sat_alt_km
