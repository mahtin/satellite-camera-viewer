.. _install:

Installation
============

Run from source tree
--------------------

Install source code locally and run from within source code tree::

	$ git clone https://github.com/mahtin/satellite-camera-viewer.git
	...
	...
	$ python -m src.SatelliteCameraViewer
	$

Run via pip install
-------------------

The install from github via pip (bypassing pypi)::

	$ pip install git+https://github.com/mahtin/satellite-camera-viewer.git
	...
	...
	$ satellitecameraviewer
	$

Or use a release file directly::

	$ RELEASE='0.4.1'
	$ pip install https://github.com/mahtin/satellite-camera-viewer/releases/download/$RELEASE/satellite_camera_viewer-$RELEASE-py3-none-any.whl
	...
	...
	$ satellitecameraviewer
	$

Run via pypi and regular pip install
------------------------------------

The most basic of installs::

	$ pip install satellite-camera-viewer
	...
	...
	$ satellitecameraviewer

Safe pip install with venv
--------------------------

Using venv will keep install clean::

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

All methods are valid, depending on your own personal setup.
