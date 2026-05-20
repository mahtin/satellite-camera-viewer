"""
SatelliteOrbit

Satellite orbit from TLE
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from astropy.time import Time
import numpy as np

from sgp4.api import Satrec, WGS72, SGP4_ERRORS

@dataclass
class SatelliteOrbit:
    """ SatelliteOrbit """
    tle: list = None

    def __post_init__(self):
        """ SatelliteOrbit """
        if self.tle is None or len(self.tle) not in [2,3] or None in self.tle:
            raise ValueError('Must provide satellite TLEs as two or three lines of text')
        if len(self.tle) == 2:
            self._sat = Satrec.twoline2rv(self.tle[0], self.tle[1], WGS72)
        else:
            self._sat = Satrec.twoline2rv(self.tle[1], self.tle[2], WGS72)

    def __str__(self):
        if len(self.tle) == 2:
            v = '["%s", "%s"]' % (self.tle[0], self.tle[1])
        else:
            v = '["%s", "%s", "%s"]' % (self.tle[0], self.tle[1], self.tle[2])
        return v

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
        # Convert datetime -> Julian date and fractional Julian date
        ts = Time(obs_time.replace(tzinfo=timezone.utc))
        # e: nonzero for any dates that produced errors, 0 otherwise.
        # r: position vectors in kilometers.
        # v: velocity vectors in kilometers per second.
        e, r_teme_km, v_teme_km_s = self._sat.sgp4(ts.jd1, ts.jd2)
        if e != 0:
            raise RuntimeError('SGP4 error value/code: %d: "%s"' % (e, SGP4_ERRORS[e]))
        # r_teme_km, v_teme_km_s are in TEME; for many RA/Dec uses, direction is close enough,
        # but for rigor you'd convert TEME -> ECI (e.g., ITRF/GCRS).
        return np.array(r_teme_km)

    def eci_velocity_vector(self, obs_time: datetime):
        """
        Returns ECI (Earth-Centered Inertial) velocity (km/s) at UTC time obs_time.
        """
        # Convert datetime -> Julian date and fractional Julian date
        ts = Time(obs_time.replace(tzinfo=timezone.utc))
        # e: nonzero for any dates that produced errors, 0 otherwise.
        # r: position vectors in kilometers.
        # v: velocity vectors in kilometers per second.
        e, r_teme_km, v_teme_km_s = self._sat.sgp4(ts.jd1, ts.jd2)
        if e != 0:
            raise RuntimeError('SGP4 error value/code: %s' % (e))
        # r_teme_km, v_teme_km_s are in TEME; for many RA/Dec uses, direction is close enough,
        # but for rigor you'd convert TEME -> ECI (e.g., ITRF/GCRS).
        return np.array(v_teme_km_s)
