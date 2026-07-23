# satellite-camera-viewer
A full sky star chart showing the view from a camera mounted on a earth orbiting satellite.


## Description
This is a Python program using `Tkinter`, `matplotlib.pyplot`, `PyVista`, and various astronomy, scientific, and satellite packages (i.e. `Astropy`, `SciPy`, and `SGP4`).
It's goal is to run a simulation of a satellite in earth orbit with an attached camera and caculate which stars would be seen in the cameras sensor.
Visualization is provided by default with camera paramaters (like focus length) being capable of being adjusted on the fly.


## Documentation and API reference

See [Satellite Camera Viewer Documentation and API reference](https://satellite-camera-viewer.readthedocs.io/) along with this README file.

## Super quick start instruction

### run from source tree

```bash
$ git clone https://github.com/mahtin/satellite-camera-viewer.git
...
...
$ python -m src.SatelliteCameraViewer
$
```

### run via pip install
```bash
$ pip install git+https://github.com/mahtin/satellite-camera-viewer.git
...
...
$ satellitecameraviewer
$
```

Or use a release file directly.

```bash
$ RELEASE='0.4.1'
$ pip install https://github.com/mahtin/satellite-camera-viewer/releases/download/$RELEASE/satellite_camera_viewer-$RELEASE-py3-none-any.whl
...
...
$ satellitecameraviewer
$
```

### run via pypi and regular pip install

```bash
$ pip install satellite-camera-viewer
...
...
$ satellitecameraviewer
```

### safe install with venv

```bash
$ mkdir ~/whatever
$ cd ~/whatever
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install git+https://github.com/mahtin/satellite-camera-viewer.git
...
...
(.venv) $ satellitecameraviewer
(.venv) $ deactivate
$
```

### healpy

The `healpy` package can be hard to install within a Windows environment. 

```bash
$ pip install 'healpy>=1.19.0'
...
  ERROR: Failed building wheel for healpy
...
$
```

The code will run without this package (and hence it's not in `requirements.txt` anymore). You will just be missing one of the FOV functions.


## Runing the software

![Satellite Camera Viewer](/img/satellite-camera-viewer.png)


## SatelliteCamera module

All the camera pointing math is done within `SatelliteCamera` and that contains it's own [[README]](src/SatelliteCameraViewer/SatelliteCamera/README.md)


## Background Concepts

### Right Ascension (RA)
Angularcoordinate on the celestial sphere analogous to longitude.  See: [Wikipedia – Right Ascension](https://en.wikipedia.org/wiki/Right_ascension)

### Declination (DEC)
Angularcoordinate analogous to latitude.  See: [Wikipedia – Declination](https://en.wikipedia.org/wiki/Declination)

### ECI / GCRS Frame
Earth‑centeredinertial coordinate system used for celestial pointing.  See: [Wikipedia – Celestial Reference System](https://en.wikipedia.org/wiki/Celestial_reference_system)

### TEME Frame
TrueEquator Mean Equinox frame used by SGP4 orbit propagator.  See: Vallado, *Fundamentals of Astrodynamics and Applications*

### Quaternion Attitude Representation
4‑componentrotation representation used for spacecraft attitude. SeeReference: [Wikipedia – Quaternion](https://en.wikipedia.org/wiki/Quaternion)

### Camera Pinhole Model
Standardoptical projection model used in computer vision and spacecraft optics.  See: [Wikipedia – Pinhole Camera Model](https://en.wikipedia.org/wiki/Pinhole_camera_model)

### HEALPix
Hierarchicalequal‑area pixelization of the sphere. See: [HEALPix](https://healpix.sourceforge.io/)

## Dependency

The `requirements.txt` file defines what works well; however, its been tested with the newest releases listed below.

```
Package             Tested     Minimum
astropy             8.0.1      7.2.0
Cartopy             0.25.0     0.25.0
matplotlib          3.11.1     3.10.0
numpy               2.5.1      2.4.0
pillow              12.3.0     12.2.0
pyvista             0.48.4     0.47.0
requests            2.34.2     2.33.0
scipy               1.18.0     1.17.0
sgp4                2.27       2.25
spherical_geometry  1.4.0      1.4.0
```

## Changelog

An automatically generated CHANGELOG is provided [here](CHANGELOG.md).

## Notes

As always, open issues or pull requests should you need via [here](https://github.com/mahtin/satellite-camera-viewer).

## Author & Copyright
Copyright (C) 2023-2026 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
