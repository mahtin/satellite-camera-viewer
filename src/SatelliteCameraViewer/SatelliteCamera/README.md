#📘 Satellite Camera RA/Dec & FOV Toolkit

##Overview
Thisrepository provides a complete, modular Python toolkit for computing **Right Ascension (RA)** and **Declination (Dec)** for every pixel in a satellite‑mounted camera.
Itsupports:

-Arbitrary satellite attitude
-Camera mounting offsets
-Multiple pointing modes
-Accurate coordinate transforms (TEME → GCRS)
-Full camera geometry (sensor size, focal length, distortion)
-Field‑of‑view (FOV) metrics
-Convex hull FOV boundaries
-HEALPix sky masks
-Star catalog integration

Thistoolkit is designed for:
-Earth‑observation satellites
-Star trackers
-Astrometry pipelines
-Spacecraft attitude determination
-Optical payload simulation
-Mission analysis and visualization

---

##Background Concepts

###Right Ascension (RA)
Angularcoordinate on the celestial sphere analogous to longitude.
Reference:[Wikipedia – Right Ascension](https://en.wikipedia.org/wiki/Right_ascension)

###Declination (Dec)
Angularcoordinate analogous to latitude.
Reference:[Wikipedia – Declination](https://en.wikipedia.org/wiki/Declination)

###ECI / GCRS Frame
Earth‑centeredinertial coordinate system used for celestial pointing.
Reference:[Wikipedia – Celestial Reference System](https://en.wikipedia.org/wiki/Celestial_reference_system)

###TEME Frame
TrueEquator Mean Equinox frame used by SGP4 orbit propagator.
Reference:Vallado, *Fundamentals of Astrodynamics and Applications*

###Quaternion Attitude Representation
4‑componentrotation representation used for spacecraft attitude.
Reference:[Wikipedia – Quaternion](https://en.wikipedia.org/wiki/Quaternion)

###Camera Pinhole Model
Standardoptical projection model used in computer vision and spacecraft optics.
Reference:[Wikipedia – Pinhole Camera Model](https://en.wikipedia.org/wiki/Pinhole_camera_model)

###HEALPix
Hierarchicalequal‑area pixelization of the sphere.
Reference:[HEALPix](https://healpix.sourceforge.io/)

---

##Camera Geometry
Thecamera is modeled using:
-Sensor size (mm)
-Focal length (mm)
-Pixel resolution
-Principal point
-Radial/tangential distortion
-Camera coordinate frame (+Z forward, +X right, +Y up)

---

##Satellite Attitude Model
Supports:
-Quaternion attitude
-Yaw/Pitch/Roll (aerospace Z‑Y‑X sequence)
-Camera mounting offsets
-Automatic nadir pointing
-Automatic velocity‑vector pointing
-Pointing at RA/Dec
-Pointing at ground lat/lon

---

##Installation
```bash
pipinstall numpy scipy astropy sgp4 healpy spherical-geometry
```

##Core Components
###CameraIntrinsics
Definessensor geometry and distortion.
###Attitude
Combinessatellite attitude + camera mounting offsets → final quaternion.
###SatelliteOrbit
LoadsTLE and propagates orbit using SGP4.
###`pixel_to_radec()`
Convertsa pixel coordinate to RA/Dec using:
-Camera geometry
-Attitude quaternion
-TEME → GCRS conversion
-SkyCoord spherical conversion
###FOVTools
-`camera_fov_metrics()`
-`camera_fov_convex_hull()`
-`camera_fov_healpix_mask()`

##Example Usage
1.Initialize Camera + Orbit + Attitude
```python
cam= CameraIntrinsics(
  sensor_size_mm=20.0,
  focal_length_mm=50.0,
  nx=4096,
  ny=4096
)

tle1= "1 25544U 98067A   20344.91667824  .00001264  00000-0  29621-4 0  9993"
tle2= "2 25544  51.6460  21.4373 0002185  93.7023  38.9384 15.49315329256545"
sat_orbit= SatelliteOrbit(tle1, tle2)

obs_time= datetime.utcnow()

attitude= Attitude(
  sat_yaw_deg=120,
  sat_pitch_deg=-10,
  sat_roll_deg=5,
  cam_yaw_deg=0,
  cam_pitch_deg=0,
  cam_roll_deg=0
)
```
2.Convert a Pixel to RA/Dec
```python
ra,dec, sat_pos = pixel_to_radec(
  px=2000,
  py=2000,
  camera=cam,
  attitude=attitude,
  obs_time=obs_time,
  sat_orbit=sat_orbit
)

print("RA:",ra, "Dec:", dec)
```
##Pointing Modes
A.Nadir Pointing
```python
r_teme_km,v_teme_km_s = sat_orbit.eci_position_velocity(obs_time)
r_gcrs_km= teme_to_gcrs_vector(r_teme_km, obs_time)

quat= quaternion_nadir_pointing(r_gcrs_km)

attitude= Attitude(sat_quat_body_to_eci=quat)

```
B.Velocity‑Vector Pointing
```python
quat= quaternion_velocity_pointing(r_gcrs_km, v_gcrs_km_s)

attitude= Attitude(sat_quat_body_to_eci=quat)

```
C.Pointing at RA/Dec
```python
quat= quaternion_pointing_radec(120.0, 22.0, obs_time)
attitude= Attitude(sat_quat_body_to_eci=quat)
```
D.Pointing at Ground Location
```python
quat= quaternion_pointing_ground(
  lat_deg=35.0,
  lon_deg=-120.0,
  obs_time=obs_time,
  r_sat_gcrs_km=r_gcrs_km
)

attitude= Attitude(sat_quat_body_to_eci=quat)
```
##Field‑of‑View Tools
###FOV Metrics
```python
metrics= camera_fov_metrics(cam, attitude, obs_time, sat_orbit)
print(metrics)
```
ConvexHull Boundary
```python
hull_coords,hull = camera_fov_convex_hull(cam, attitude, obs_time, sat_orbit)
```
HEALPixMask
```python
mask,pix = camera_fov_healpix_mask(cam, attitude, obs_time, nside=64)
```

##References
-Astropy Project — https://www.astropy.org
-SGP4 Orbit Propagator — https://pypi.org/project/sgp4
-HEALPix — https://healpix.sourceforge.io
-Pinhole Camera Model — https://en.wikipedia.org/wiki/Pinhole_camera_model
-Celestial Coordinates — https://en.wikipedia.org/wiki/Celestial_coordinate_system
-Quaternion Rotations — https://en.wikipedia.org/wiki/Quaternion
