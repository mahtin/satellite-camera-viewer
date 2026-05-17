# satellite-camera-viewer
A full sky star chart showing the view from a camera mounted on a earth orbiting satellite.

## Description
This is a Python program using `Tkinter`, `matplotlib.pyplot`, `PyVista`, and various astronomy, scientific, and satellite packages (i.e. `Astropy`, `SciPy`, and `SGP4`).
It's goal is to run a simulation of a satellite in earth orbit with an attached camera and caculate which stars would be seen in the cameras sensor.
Visualization is provided by default with camera paramaters (like focus length) being capable of being adjusted on the fly.

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
$ cd .venv
$ source .venv/bin/activate
(.venv) $ pip install git+https://github.com/mahtin/satellite-camera-viewer.git
...
...
(.venv) $ satellitecameraviewer
(.venv) $ deactivate
$
```

## Runing the software

![Satellite Camera Viewer](/img/satellite-camera-viewer.png)

## SatelliteCamera module

All the camera pointing math is done within `SatelliteCamera` and that contains it's own [[README]](src/SatelliteCameraViewer/SatelliteCamera/README.md)

## Changelog

An automatically generated CHANGELOG is provided [here](CHANGELOG.md).

## Notes

As always, open issues or pull requests should you need via [here](https://github.com/mahtin/satellite-camera-viewer).

## Author & Copyright
Copyright (C) 2023-2026 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
