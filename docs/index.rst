..
  Copyright (C) 2023-2026 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin

.. SatelliteCameraViewer

SatelliteCameraViewer
=====================

**SatelliteCameraViewer** is a full sky star chart showing the view from a camera mounted on a earth orbiting satellite.

Release v\ |version|. (:ref:`Installation <install>`)

.. image:: https://img.shields.io/pypi/v/satellite-camera-viewer.svg?maxAge=86400
    :target: https://pypi.org/project/satellite-camera-viewer/
    :alt: PyPI Version Badge

.. image:: https://img.shields.io/pypi/pyversions/satellite-camera-viewer.svg
    :target: https://pypi.org/project/satellite-camera-viewer/
    :alt: Supported Versions Badge

.. image:: https://static.pepy.tech/badge/satellite-camera-viewer/month
    :target: https://pepy.tech/project/satellite-camera-viewer
    :alt: Downloads Per Month Badge

.. image:: https://img.shields.io/github/contributors/psf/satellite-camera-viewer.svg
    :target: https://github.com/psf/satellite-camera-viewer/graphs/contributors
    :alt: Contributors Badge

.. image:: https://readthedocs.org/projects/satellite-camera-viewer/badge/?version=latest
    :target: https://satellite-camera-viewer.readthedocs.io
    :alt: Documentation Badge

Description
-----------

**SatelliteCameraViewer** is a Python program using `Tkinter`, `matplotlib.pyplot`, `PyVista`, and various astronomy, scientific, and satellite packages (i.e. `Astropy`, `SciPy`, and `SGP4`).
It's goal is to run a simulation of a satellite in earth orbit with an attached camera and caculate which stars would be seen in the cameras sensor.
Visualization is provided by default with camera paramaters (like focus length) being capable of being adjusted on the fly.

Install Guide
-------------

Install is via standard Python methods; however, you can also install from source or github directly. See specific install pages below.

.. toctree::
   :maxdepth: 2

   install

Modules etc
-----------

Everything starts with `SatelliteCameraViewer` and the `viewer.py` file. The camera, satellite 3d image, star display, and controls are kicked off from there.

.. toctree::
   :maxdepth: 1

   All modules <modules>
   SatelliteCameraViewer <SatelliteCameraViewer>
   CameraImage <SatelliteCameraViewer.CameraImage>
   Cubesat <SatelliteCameraViewer.Cubesat>
   SatelliteCamera <SatelliteCameraViewer.SatelliteCamera>
   StarCatalog <SatelliteCameraViewer.StarCatalog>

Index
-----

* :ref:`genindex`
* :ref:`modindex`
