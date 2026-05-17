"""
fits_stars.py

Star catalog from FITS
"""

from datetime import datetime
from astropy.io import fits
from astropy.coordinates import SkyCoord, GCRS
from astropy.time import Time
import astropy.units as u

from .CameraIntrinsics import CameraIntrinsics
from .CameraAttitude import CameraAttitude

def load_star_catalog_from_fits(fits_path: str, ra_col: str = "RA", dec_col: str = "DEC"):
    """
    Load a simple star catalog from a FITS table.
    Assumes columns named RA/DEC (or user-specified) in degrees.
    Returns an astropy SkyCoord object.
    """
    with fits.open(fits_path) as hdul:
        data = hdul[1].data  # typical for FITS tables
        ra = data[ra_col]
        dec = data[dec_col]

    # Use ICRS as there's no time represented yet - convert later
    return SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs")

def today_stars(stars_icrs, obs_time: datetime):
    """ today_stars """
    stars_gcrs = stars_icrs.transform_to(GCRS(obstime=Time(obs_time)))
    return stars_gcrs

def match_stars_in_image(camera: CameraIntrinsics, attitude: CameraAttitude, obs_time: datetime, star_catalog: SkyCoord, px_grid_step: int = 200):
    """
    Very rough scaffold:
    - Sample a grid of pixels across the image
    - Convert each to RA/Dec
    - Compare to catalog to see which stars fall near those directions

    This is NOT a full plate-solver; it's just a starting point.
    """
    coords_image = []
    px_list = []
    py_list = []

    for px in range(0, camera.nx, px_grid_step):
        for py in range(0, camera.ny, px_grid_step):
            ra_deg, dec_deg, _ = camera.pixel_to_radec(
                px, py, camera, attitude, obs_time, sat_orbit=None
            )
            coords_image.append((ra_deg, dec_deg))
            px_list.append(px)
            py_list.append(py)

    coords_image = SkyCoord(
        ra=[c[0] for c in coords_image] * u.deg,
        dec=[c[1] for c in coords_image] * u.deg,
        frame="icrs",
    )

    # For each image direction, find nearest star in catalog
    idx, sep2d, _ = coords_image.match_to_catalog_sky(star_catalog)

    # Return matches with separation info
    matches = []
    for i in range(len(coords_image)):
        matches.append(
            {
                "px": px_list[i],
                "py": py_list[i],
                "image_coord": coords_image[i],
                "star_coord": star_catalog[idx[i]],
                "separation_arcsec": sep2d[i].arcsec,
            }
        )

    return matches
