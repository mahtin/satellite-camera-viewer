""" core """

import math
from datetime import datetime

import numpy as np
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
from astropy.coordinates import SkyCoord
import astropy.units as u

from .SatelliteCamera import SatelliteCameraError
from .Constellations import ConstellationDatabase
from .MyCamera import MyCamera
from .DoCameraImage import DoCameraImage
from .DoCubesatViewer import DoCubesatViewer
from .PaintStarsConstellationsBSC5 import PaintStarsConstellationsBSC5
from .PaintSunMoonPlanets import PaintSunMoonPlanets
from .PaintConstellation import PaintConstellation

from .ui import UserInterface
from .misc import arcseconds_to_radians, ra_fix, mag_map, split_plot_mollweide_line_ra_dec_deg, split_plot_mollweide_line
from .stars_in_polygon_icrs import stars_in_polygon_icrs
from .static_list_satellites import static_list_satellites

#
# Do this to debug:
# .../matplotlib/projections/geo.py:397: RuntimeWarning: invalid value encountered in arcsin
# theta = np.arcsin(y / np.sqrt(2))

class CoreCode:
	"""
	CoreCode - the core drawing code for the stars - also includes logic for the user interface

	:param ui: User interface class
	:type root: UserInterface
	"""

	_TIMER_SLEEP_ACCELERATE = 500			# when running in accelerate mode - only sleep for a short while
	_TIMER_SLEEP_NORMAL = 5000			# normal mode is a redo every five seconds - but this should be orbit based

	_TIME_JUMP_ACCELERATE = 24*60*60		# accelerate means jump ahead by 1 hour
	_TIME_JUMP_ACCELERATE = 2 * 60			# accelerate means jump ahead by 2 mins

	# https://matplotlib.org/stable/gallery/color/named_colors.html#css-colors
	_COLORS = {
		'fig-facecolor': '#ebebeb',
		'sky-facecolor': 'whitesmoke',
		'sky-grid': 'lightgrey',
		'sky-axis': 'dimgrey',
		'sky-label': 'black',
		'sky-ecliptic': 'dimgrey',
		'sky-galactic': 'saddlebrown',
		'earth-facecolor': 'whitesmoke',
		'earth-coastline': 'lightgrey',
		'earth-grid': 'lightgrey',
		'earth-marker': 'red',
		'earth': 'red',
		'plot-center': 'darkgreen',
		'plot-corners': 'darkblue',
		'plot-polygon': 'orange',
		'plot-hull': 'orange',
		'plot-pixels': 'cornflowerblue',
		'plot-pixels-corner': 'royalblue',
		'stars': 'black',
		'stars-found': 'magenta',
		'constellations': 'red',
		'constellations-boundaries': 'royalblue',
		'sun': 'darkorange',
		'moon': 'dimgrey',
		'planets': 'blue',
		'match': 'red',
	}

	# Orion and Sagittarius because they are not next to each other
	_DEFAULT_CONSTELLATIONS = [
		'Ori',
		'Sgr'
	]
	# Camera stuff
	_DEFAULT_CAMERA_NAME = 'Nikon D5'
	_DEFAULT_FOCAL_LENGTH = 50

	# debug etc
	_verbose = False

	def __init__(self, ui:UserInterface=None):
		"""
		CoreCode - the core drawing code for the stars - also includes logic for the user interface

		:param ui: User interface class
		:type ui: UserInterface
		"""
		if ui is None:
			raise ValueError('CoreCode() needs ui value') from None
		self.ui = ui
		# register ourselves with the UI - that way ui knows core and core knows ui
		self.ui.core = self

		self._timer_id = None

		self._satellite_name = static_list_satellites[0].name

		# pointing
		self._pointing = 'vv'

		# stars
		self._mag = 5.0

		# camera (note that defaults are the same in the lower level functions)
		camera_name = self._DEFAULT_CAMERA_NAME
		focal_length_mm = self._DEFAULT_FOCAL_LENGTH
		self.my_camera = MyCamera(satellite_name=self._satellite_name, camera_name=camera_name, focal_length_mm=focal_length_mm)

		# switches
		self._switch_accelerate_time = False
		self._switch_stars = False
		self._switch_match_stars = False
		self._switch_earth_vector = False
		self._switch_planets_etc = False
		self._switch_constellation_boundaries = False

		self._items_plotted = []
		self._starfield_centerline_plot = None
		self._starfield_centerline_data = None
		self._earthtrack = []
		self._earthtrack_plot = None
		self._earthtrack_mark = None

		# start the plotting...
		self._setup_plot()

		# plotted elements - this is just the setup - they are enabled/disabled via the UI
		self._sun_moon_planets = PaintSunMoonPlanets(
			self._starfield_ax,
			self._COLORS['sun'],
			self._COLORS['moon'],
			self._COLORS['planets'],
			self._COLORS['sky-galactic'],
			self._COLORS['sky-ecliptic'],
			fontdict={'fontsize':self.ui.font['size']+2}
		)
		self._constellation_boundaries = PaintConstellation(self._starfield_ax, color=self._COLORS['constellations-boundaries'])
		self._scbsc5 = PaintStarsConstellationsBSC5(self._starfield_ax, self._COLORS['stars'], self._COLORS['constellations'], self._DEFAULT_CONSTELLATIONS, mag=self._mag)

	def _setup_plot(self):
		""" _setup_plot """
		# starfield plot
		self._create_starfield_subplot()
		self._paint_starfield_axis()
		# earth plot
		self._create_earth_subplot()
		self._paint_earth_axis()

	def plot_in_tk(self, parent, which, row=0, col=0, padx=0, pady=0, sticky='nsew'):
		""" plot_in_tk """
		if which == 'earth':
			fig = self._earth_fig
		elif which == 'starfield':
			fig = self._starfield_fig
		else:
			raise ValueError('%s: invalid which value in plot_in_tk()' % (which)) from None

		canvas = FigureCanvasTkAgg(fig, master=parent)
		canvas.get_tk_widget().grid(row=row, column=row, padx=padx, pady=pady, sticky=sticky)

		if which == 'earth':
			self._earth_canvas = canvas
		elif which == 'starfield':
			self._starfield_canvas = canvas
		else:
			raise ValueError('%s: invalid which value in plot_in_tk()' % (which)) from None

		canvas.draw()

	def cubesat_viewer_register(self, u=3, label=None, w=400, h=300):
		"""
		cubesat_viewer_register - setup Cubesat.
		"""
		self._cv = DoCubesatViewer(u=u, label=label, w=w, h=h)

	def camera_image_register(self, label=None, nx=400, ny=300, w=400, h=300):
		"""
		camera_image_register - setup Camera Image.
		"""
		self._ci = DoCameraImage(label=label, nx=nx, ny=ny, w=w, h=h)

	def _create_starfield_subplot(self):
		""" _create_starfield_subplot - core logic to build the pyplot area. """
		# plt.style.use('classic')
		# plt.rcParams['toolbar'] = 'None'	# was 'toolbar2' but we don't need the controls
		self._starfield_fig = Figure(figsize=(14.0, 7.04), dpi=65, layout='tight')
		self._starfield_fig.patch.set_linewidth(0)
		self._starfield_fig.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
		self._starfield_fig.set_layout_engine(layout='tight')
		self._starfield_fig.patch.set_facecolor(self._COLORS['fig-facecolor'])
		# projection='mollweide' is an equal-area, pseudocylindrical projection where parallels are straight lines.
		self._starfield_ax = self._starfield_fig.add_subplot(1, 1, 1, projection='mollweide')
		self._starfield_ax.set_facecolor(self._COLORS['sky-facecolor'])

	def _paint_starfield_axis(self):
		""" _paint_starfield_axis - x and y axis (which is really ra and dec). """
		# match font to rest of user interface (and hence system)
		font_size = self.ui.font['size']
		# grid lines
		self._starfield_ax.grid(color=self._COLORS['sky-grid'], alpha=0.5)
		# x axis (ra)
		# 24 hours is 360 degrees - one hour is 15 degrees. Mark every other hour (i.e 30 degrees)
		# note that this projection is -180 to +180 - we need to handle that later on - for now we simply change the lables
		# When dealing with astronomical coordinates the right ascension increases eastward, located conventionally left on celestial charts.
		x_values = [math.radians(v) for v in range(-180,180+30,30)]
		x_labels = ['', '10h','8h','6h','4h','2h','0h','22h','20h','18h','16h','14h', '']
		self._starfield_ax.set_xticks(x_values, x_labels, rotation='vertical', color=self._COLORS['sky-axis'], alpha=0.5,
			fontdict={'fontsize':font_size, 'horizontalalignment':'center', 'verticalalignment':'center'}
		)
		self._starfield_ax.set_xlabel('Right Ascension (hours)', color=self._COLORS['sky-label'],
			fontdict={'fontsize':font_size, 'horizontalalignment':'center', 'verticalalignment':'top'}
		)

		# y axis (dec)
		y_values = [math.radians(v) for v in range(-90,90+10,10)]
		y_labels = [str(v) for v in range(-90,90+10,10)]
		# remove 90 and 80 and -80 and -90 (as they don't draw correctly - and aren't needed)
		for ii in [0, 1, -1, -2]:
			y_labels[ii] = ''
		self._starfield_ax.set_yticks(y_values, y_labels, color=self._COLORS['sky-axis'],
			fontdict={'fontsize':font_size, 'horizontalalignment':'center', 'verticalalignment':'center'}
		)
		self._starfield_ax.set_ylabel('Declination (degrees)', color=self._COLORS['sky-label'],
			fontdict={'fontsize':font_size, 'horizontalalignment':'right', 'verticalalignment':'center'}
		)

	def _create_earth_subplot(self):
		""" _create_earth_subplot - core logic to build the pyplot area. """
		self._earth_fig = Figure(figsize=(3.0, 3.00), dpi=65, layout='tight')
		self._earth_fig.patch.set_linewidth(0)
		self._earth_fig.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
		self._earth_fig.set_layout_engine(layout='tight')
		self._earth_fig.patch.set_facecolor(self._COLORS['fig-facecolor'])
		self._earth_ax = self._earth_fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
		self._earth_ax.set_facecolor(self._COLORS['earth-facecolor'])

	def _paint_earth_axis(self):
		""" _paint_earth_axis - x and y axis. """
		#self._earth_ax.set_extent([-180, 180, -90, 90], crs=projection())
		self._earth_ax.set_global()
		self._earth_ax.stock_img() # this is a bit excessive - but when has that stopped us?
		self._earth_ax.coastlines(resolution='110m', color=self._COLORS['earth-coastline'])
		self._earth_ax.grid(color=self._COLORS['earth-grid'], alpha=0.5)
		#self._earth_ax.gridlines(draw_labels=True)
		# self._earth_ax.get_xaxis().set_visible(False)
		# self._earth_ax.get_yaxis().set_visible(False)

	def update_starfield_and_more(self):
		""" update_starfield_and_more - primary logic to redraw the sky plot. """
		# Key Details for Mollweide Projection in Matplotlib:
		# Input Data Formats: Data must be in radians, not degrees, for proper positioning
		# X-Axis (Longitude): Ranges from -PI to +PI
		# Y-Axis (Latitude): Ranges from -PI/2 to +PI/2
		# Plotting with longitude (x) and latitude (y) in radians
		# plt.plot(lon_in_radians, lat_in_radians)

		# clean up from previous run
		self.items_plotted_clear()
		# center
		self.plot_starfield_centerline_data()
		self.plot_starfield_centerline()

		self.do_pointing()

		# border
		p = self.plot_border_vectors()
		self.items_plotted_add(p)

		# camera view /box/polygon
		show_box = False
		show_poly = False
		show_hull = False
		if show_box:
			# A box does not show edges correctly
			p = self.plot_corners()
			self.items_plotted_add(p)
		if show_poly:
			# Four dots in the corners
			p = self.plot_polygons()
			self.items_plotted_add(p)
		if show_hull:
			p = self.plot_hull()
			self.items_plotted_add(p)

		# a matrix of pixels (1 negates it)
		p = self.plot_pixels(nsteps=1)
		self.items_plotted_add(p)

		if self._switch_stars and self._switch_match_stars:
			self.do_match()

		if self._switch_earth_vector:
			# TODO - this is debug only at present
			v1 = self.my_camera.earth_center_vector()
			v2 = self.my_camera.earth_center_vector_icrs()
			earth_ra_deg, earth_dec_deg = self.my_camera.earth_center_radec_simple()
			cam_earth_ra_deg, cam_earth_dec_deg = self.my_camera.earth_center_radec()
			print('Earth: vector = [%6.3f, %6.3f, %6.3f] %s' % (v1[0], v1[1], v1[2], str(v2).replace('\n',' ')), end='')
			print(' ra,dec = [%6.2f,%6.2f] [%6.2f,%6.2f]' % (earth_ra_deg, earth_dec_deg, cam_earth_ra_deg, cam_earth_dec_deg))

		# finally, show where we are at
		self.do_info()

	def do_pointing(self):
		""" do_pointing """
		# adjust camera/satellite attitude
		if self._pointing == 'vv':
			# follow satellite path (it's velocity vector)
			self.my_camera.camera.choose_attitude(
				self._pointing,
				# XYZ for satellite == set by vv (velocity vector)
				# XYZ for camera == roll, pitch, yaw
				# but cubesat implements the camera on the +Y side - TODO
				cam_yaw_deg=self.ui.rpy_values_deg['roll'],
				cam_pitch_deg=self.ui.rpy_values_deg['pitch'],
				cam_roll_deg=self.ui.rpy_values_deg['yaw'],
			)
		else:
			self.my_camera.camera.choose_attitude(
				self._pointing,
				# XYZ for satellite == roll, pitch, yaw
				sat_yaw_deg=self.ui.rpy_values_deg['roll'],
				sat_pitch_deg=self.ui.rpy_values_deg['pitch'],
				sat_roll_deg=self.ui.rpy_values_deg['yaw'],
				# XYZ for camera == roll, pitch, yaw
				cam_yaw_deg=0.0,
				cam_pitch_deg=90.0,	# Cubesat implements the camera on the +Y side
				cam_roll_deg=0.0,
			)

		# other forms of pointing - yet to be coded
		#self.my_camera.camera.choose_attitude('star', star_ra_deg=100, star_dec_deg=70)
		#self.my_camera.camera.choose_attitude('nadir')
		#self.my_camera.camera.choose_attitude('ground', earth_lat_deg=36.974117, earth_lon_deg=-122.030792)

	def do_match(self):
		""" do_match """
		# Star chart
		if False:
			p = self.plot_matched_closest_star()
			if p:
				self.items_plotted_add(p)
		# Camera
		p = self.camera_image_matched_stars()
		if p:
			self.items_plotted_add(p)

		return
		# Earth intercept (maybe)
		earth_ra_deg, earth_dec_deg = self.my_camera.earth_center_radec_simple()
		earth_radius_deg = self.my_camera.earth_angular_radius()
		earth_ra_rad = math.radians(float(earth_ra_deg))
		earth_dec_rad = math.radians(float(earth_dec_deg))
		earth_ra_rad = ra_fix([earth_ra_rad])[0]
		# s = ... TODO
		s = earth_radius_deg * 3.0 * self._starfield_fig.dpi
		p = self._starfield_ax.scatter([earth_ra_rad], [earth_dec_rad], facecolors='none', edgecolors=self._COLORS['earth'], alpha=1.0, s=s)
		self.items_plotted_add(p)
		try:
			earth_points_deg = self.my_camera.camera_fov_intercept_earth(border_step=10)
			print('camera_fov_intercept_earth():', 'len(earth_points_deg) =', len(earth_points_deg))
			_ = self.plot_earth_outline(earth_points_deg)
			# pixels = self.my_camera.camera_fov_intercept_earth()
			# print('camera_fov_intercept_earth():', 'pixels =', pixels)
		except SatelliteCameraError:
			pass

	def do_info(self):
		""" do_info """
		# Lat, long & altitude of satellite
		sat_lon_deg, sat_lat_deg, sat_alt_km = self.my_camera.sat_lon_lat_alt()
		self.plot_earthtrack_dot(sat_lon_deg, sat_lat_deg)

		earth_ra_deg, earth_dec_deg = self.my_camera.earth_center_radec_simple()
		earth_radius_deg = self.my_camera.earth_angular_radius()
		
		# Shadow ?
		shadow = self.my_camera.sat_in_eclipse()

		# build return string - showing camera info
		angular_width, angular_height, solid_angle_steradians = self.my_camera.camera_fov_angular_width_height()

		s = ''
		s += '[%5.1f,%5.1f] %5.1f Km | %s\n' % (sat_lon_deg, sat_lat_deg, sat_alt_km, self.my_camera.observed_time)
		s += '%s\n' % (str(self.my_camera.camera))
		s += '[%5.1f,%5.1f] @ %5.1f Km radius | %.1f deg width by %.1f deg height |' % (earth_ra_deg, earth_dec_deg, earth_radius_deg, angular_width, angular_height)
		s += ' %.1f%% of whole sky' % (100.0*solid_angle_steradians/(4*math.pi))
		if shadow:
			s += ' | shadow'
		self.ui.camera_info(s)

	def plot_earth_outline(self, earth_points_deg):
		""" plot_earth_outline - add outline of earth to the sky plot. """
		ra_rad = [math.radians(float(v[0])) for v in earth_points_deg]
		dec_rad = [math.radians(float(v[1])) for v in earth_points_deg]
		ra_rad = ra_fix(ra_rad)
		return self._starfield_ax.plot(ra_rad, dec_rad, label='Earth Outline', alpha=0.25, color=self._COLORS['earth'], linewidth=4.0)

	def plot_earthtrack_dot(self, lon_deg:float, lat_deg:float):
		""" plot_earthtrack_dot """
		# We significantly round down because the earth map is tiny on the screen and we don't need many decimal places
		lon_deg = float(lon_deg.round(1))
		lat_deg = float(lat_deg.round(1))
		self._earthtrack = self._earthtrack[-63:]
		if len(self._earthtrack) == 0 or self._earthtrack[-1] != (lon_deg, lat_deg):
			self._earthtrack.append((lon_deg, lat_deg))

		if self._earthtrack_plot is None:
			self._earthtrack_plot = self._earth_ax.plot(self._earthtrack, color=self._COLORS['earth-marker'], alpha=0.5, linewidth=2.0, transform=ccrs.Geodetic())
			self._earthtrack_mark = self._earth_ax.plot(lon_deg, lat_deg, color=self._COLORS['earth-marker'], alpha=1.0, marker='o', markersize=6, transform=ccrs.Geodetic())
		else:
			self._earthtrack_plot[0].set_data([v[0] for v in self._earthtrack], [v[1] for v in self._earthtrack])
			self._earthtrack_mark[0].set_data([lon_deg], [lat_deg])

	def plot_earthtrack_dot_clear(self):
		""" plot_earthtrack_dot_clear """
		self._earthtrack = []
		if self._earthtrack_plot is not None:
			self._earthtrack_plot[0].set_data([], [])
			self._earthtrack_mark[0].set_data([], [])

	def draw(self):
		""" draw - flush everything to the screen. """
		self._starfield_canvas.draw()
		self._earth_canvas.draw()

	def items_plotted_clear(self):
		""" items_plotted_clear """
		if len(self._items_plotted) == 0:
			return
		for p in self._items_plotted:
			if isinstance(p, PathCollection):
				p.remove()
			elif isinstance(p, list):
				p[0].remove()
		self._items_plotted = []

	def items_plotted_add(self, p):
		""" items_plotted_add """
		if isinstance(p, list):
			self._items_plotted += p
		else:
			self._items_plotted.append(p)

	def plot_starfield_centerline_data(self):
		""" plot_starfield_centerline_data """
		ra_deg, dec_deg = self.my_camera.pixel_to_radec(self.my_camera.camera.nx/2, self.my_camera.camera.ny/2)
		ra_rad = math.radians(ra_deg)
		dec_rad = np.array([math.radians(dec_deg)])
		ra_rad = ra_fix(np.array([ra_rad]))
		new_data = np.array([np.array([ra_rad[0], dec_rad[0]])])
		if self._starfield_centerline_data is None:
			self._starfield_centerline_data = new_data
		else:
			self._starfield_centerline_data = np.append(self._starfield_centerline_data, new_data, axis=0)

	# we keep this one on the screen - so processed differently
	def plot_starfield_centerline(self):
		""" plot_starfield_centerline """
		if self._starfield_centerline_plot is None:
			# this is an empty plot
			p = self._starfield_ax.plot([], [], color=self._COLORS['plot-center'], alpha=1.0, linewidth=1.5, zorder=10)
			self._starfield_centerline_plot = p
		if self._starfield_centerline_data is None:
			return
		# trim data (63 is a random number)
		self._starfield_centerline_data = self._starfield_centerline_data[-63:]

		# print('center_line_data =', np.degrees(self._starfield_centerline_data))
		# self._starfield_centerline_plot[0].set_data(self._starfield_centerline_data[:, 0], self._starfield_centerline_data[:, 1])
		segments = split_plot_mollweide_line(np.degrees(self._starfield_centerline_data[:, 0]), np.degrees(self._starfield_centerline_data[:, 1]))
		# TODO - off by one error still!
		all_ra_rad = []
		all_dec_rad = []
		for ra_rad, dec_rad in segments:
			# ra_rad = ra_fix(ra_rad)
			all_ra_rad.extend(ra_rad[1:])
			all_dec_rad.extend(dec_rad[1:])
			if len(all_ra_rad) == 1:
				all_ra_rad.extend(ra_rad)
				all_dec_rad.extend(dec_rad)
			all_ra_rad.append(np.nan)
			all_dec_rad.append(np.nan)
		# print('all_ra_rad =', np.degrees(all_ra_rad))
		# print('all_dec_rad =', np.degrees(all_dec_rad))
		self._starfield_centerline_plot[0].set_data(all_ra_rad, all_dec_rad)

	def plot_starfield_centerline_clear(self):
		""" plot_starfield_centerline_clear """
		self._starfield_centerline_data = None
		self._starfield_centerline_plot[0].set_data([], [])

	def plot_corners(self):
		""" plot_corners """
		box, _ = self.my_camera.camera_fov_radec_box()
		corners = [
			box['top_left'],
			box['top_right'],
			box['bottom_right'],
			box['bottom_left'],
			box['top_left'],	# close rectangle back to first point
		]
		ra_rad = [math.radians(v['ra_deg']) for v in corners]
		dec_rad = [math.radians(v['dec_deg']) for v in corners]
		ra_rad = ra_fix(ra_rad)
		# not fixed for wrap yet
		p = self._starfield_ax.plot(ra_rad, dec_rad, color=self._COLORS['plot-corners'], alpha=0.25, linewidth=3.0, linestyle='dashed')
		return p

	def plot_polygons(self):
		""" plot_polygons """
		_, polygon = self.my_camera.camera_fov_radec_box()
		ra_rad = [math.radians(float(v)) for v in polygon[0]]
		dec_rad = [math.radians(float(v)) for v in polygon[1]]
		ra_rad = ra_fix(ra_rad)
		p = self._starfield_ax.scatter(ra_rad, dec_rad, color=self._COLORS['plot-polygon'], alpha=0.5, s=40.0)
		return p

	def plot_hull(self):
		""" plot_hull """
		hull_coords, _ = self.my_camera.camera_fov_convex_hull()
		ra_rad = [math.radians(float(v)) for v in hull_coords[0]]
		dec_rad = [math.radians(float(v)) for v in hull_coords[1]]
		ra_rad = ra_fix(ra_rad)
		# not fixed for wrap yet
		p = self._starfield_ax.plot(ra_rad, dec_rad, color=self._COLORS['plot-hull'], alpha=0.15, linewidth=2.0, linestyle='solid')
		return p

	def plot_pixels(self, nsteps=3):
		""" plot_pixels """
		pixels = self.my_camera.sensor_to_radec(nsteps=nsteps)
		ra_rad = [math.radians(v[0]) for v in pixels.values()]
		dec_rad = [math.radians(v[1]) for v in pixels.values()]
		ra_rad = ra_fix(ra_rad)
		# all points
		p3 = self._starfield_ax.scatter(ra_rad, dec_rad, color=self._COLORS['plot-pixels'], alpha=0.75, s=20.0)
		# learing left point/corner
		p1 = self._starfield_ax.scatter(ra_rad[nsteps:nsteps+1], dec_rad[nsteps:nsteps+1], color=self._COLORS['plot-pixels-corner'], alpha=1.0, s=100.0)
		# learing right point/corner
		p2 = self._starfield_ax.scatter(ra_rad[-1:], dec_rad[-1], color=self._COLORS['plot-pixels-corner'], alpha=1.0, s=100.0)
		return [p1,p2,p3]

	def plot_border_vectors(self):
		""" plot_border_vectors """
		border_vectors = self.my_camera.camera_fov_border_vectors_radec_deg(border_step=25)

		plots = []
		for ra_rad, dec_rad in split_plot_mollweide_line_ra_dec_deg(border_vectors):
			ra_rad = ra_fix(ra_rad)
			p = self._starfield_ax.plot(ra_rad, dec_rad, color='red', alpha=1.0, linewidth=1.5, linestyle='solid')
			plots.append(p)
		return plots

	def _match_stars_in_polygon(self):
		""" match_stars_in_polygon """
		# look for stars ...
		polygon_gcrs = self.my_camera.camera_fov_border_vectors(border_step=10)
		c = SkyCoord(ra=polygon_gcrs.ra.value*u.deg, dec=polygon_gcrs.dec.value*u.deg, frame='icrs')
		xyz = c.cartesian.xyz.value
		border_vectors = xyz.T   # shape (N,3)

		inside_mask = stars_in_polygon_icrs(self._scbsc5.vector, border_vectors)

		found_stars = self._scbsc5.skycoords[inside_mask]
		return found_stars, inside_mask

	def camera_image_matched_stars(self):
		""" camera_image_matched_stars """
		# now find all stars inside camara view ...
		found_stars, inside_mask = self._match_stars_in_polygon()
		if len(found_stars) == 0:
			#  paint an empty image
			self._ci.stars()
			return None

		start_t = datetime.now()
		# all the stars (will be masked before use)
		stars_ra_rad, stars_dec_rad, stars_mag = self._scbsc5.get_stars()
		stars_ra_rad = stars_ra_rad[inside_mask]
		stars_dec_rad = stars_dec_rad[inside_mask]
		stars_mag = stars_mag[inside_mask]

		# camera image

		def build_xy_list(found_stars):
			""" build_xy_list """
			xy_list = []
			for star in found_stars:
				ra_deg = star.ra.degree
				dec_deg = star.dec.degree
				try:
					px, py = self.my_camera.radec_to_pixel(ra_deg, dec_deg)
				except SatelliteCameraError:
					# outside the view of the camera - should not happen if polygon is accurate
					continue
				xy_list.append((px,py))
			if len(found_stars) != len(xy_list):
				print('build_xy_list():', len(found_stars), '!=', len(xy_list))
			return xy_list

		xy_list = build_xy_list(found_stars)
		elapsed_t = datetime.now() - start_t
		print('camera_image_matched_stars(): time:', self._mag, len(found_stars), (elapsed_t.seconds*1000.0 + elapsed_t.microseconds/1000.0), 'msec')

		self._ci.stars(xy_list=xy_list, mag_list=stars_mag)

		def build_mag_bucket_list(stars_mag):
			""" build_mag_bucket_list """
			bucket = {}
			for mag in stars_mag:
				try:
					bucket[int(mag)] += 1
				except KeyError:
					bucket[int(mag)] = 1
			s = sorted(['%d:%d' % (k, v) for k,v in bucket.items()])
			return '[' + ', '.join(s) + ']'

		s = 'Camera image has %d stars' % len(found_stars)
		s += '\nMagnitude: ' + build_mag_bucket_list(stars_mag)
		self.ui.misc_text(s)

		stars_ra_rad = ra_fix(stars_ra_rad)
		stars_size_pixels = mag_map(stars_mag)
		# plot
		p1 = self._starfield_ax.scatter(stars_ra_rad, stars_dec_rad, s=stars_size_pixels, alpha=1, color=self._COLORS['stars-found'], zorder=5)
		return p1

	def plot_matched_closest_star(self):
		""" plot_matched_closest_star """
		# look for matched (closest) star
		matches = self._match_against_bsc5()

		ra_rad = []
		dec_rad = []
		for m in matches:
			center_ra_rad = m['coords'].ra.radian
			center_dec_rad = m['coords'].dec.radian
			star_ra_rad = m['star_coord'].ra.radian
			star_dec_rad = m['star_coord'].dec.radian
			star = matches[0]['bsc5']
			if star.constellation:
				c = ConstellationDatabase.fullmatch(star.constellation)
				c = c[0].constellation + ' (' + c[0].meaning + ')'
			else:
				c = None

			s = 'camera [%.1f,%.1f] deg\n  star [%.1f,%.1f] deg +/- %.3f deg\n       %s%s @ %.1f mag' % (
				math.degrees(center_ra_rad), math.degrees(center_dec_rad),
				math.degrees(star_ra_rad), math.degrees(star_dec_rad),
				math.degrees(arcseconds_to_radians(m['separation_arcsec'])),
				star.name if star.name else '-',
				' in ' + c if c else '',
				star.mag
			)
			self.ui.star_found_text(s)

			ra_rad.append(center_ra_rad)
			dec_rad.append(center_dec_rad)
			ra_rad.append(star_ra_rad)
			dec_rad.append(star_dec_rad)
			# TODO - only one for now
			break

		# TODO powered down for now - does not unpaint itself (yet)
		if self._switch_stars and self._switch_match_stars:
			star = matches[0]['bsc5']
			diameter = mag_map(star.mag, multiplier=4.0)
			ra_rad = ra_fix(ra_rad)
			p1 = self._starfield_ax.plot(ra_rad, dec_rad, label='Star match', alpha=1.0, color=self._COLORS['match'], linewidth=3.0)
			p2 = self._starfield_ax.scatter(ra_rad[-1:], dec_rad[-1:], facecolors='none', edgecolors=self._COLORS['match'], s=diameter)
			p3 = self._starfield_ax.scatter(ra_rad[0:1], dec_rad[0:1], facecolors=self._COLORS['plot-center'], edgecolors=self._COLORS['plot-center'], s=60)
			return [p1, p2, p3]
		return None

	def do_match_stars(self, value):
		""" do_match_stars """
		self._switch_match_stars = value
		if self._switch_match_stars:
			# also show stars if not showing
			self._do_stars_real(False)
			self.ui.stars_button_set(True)
			self._do_stars_real(True)
		else:
			self._ci.reset()
			s = ''
			self.ui.star_found_text(s)
			self.ui.misc_text(s)

	def do_planets_etc(self, value):
		""" do_planets_etc """
		self._switch_planets_etc = value
		self._sun_moon_planets.change(self._switch_planets_etc, self.my_camera.observed_time, self.my_camera.camera.eci_position_vector)
		self.draw()

	def do_constellation_boundaries(self, value):
		""" do_constellation_boundaries """
		self._switch_constellation_boundaries = value
		self._constellation_boundaries.change(self._switch_constellation_boundaries)
		self.draw()

	def do_earth_vector(self, value):
		""" do_earth_vector """
		self._switch_earth_vector = value

	def do_mag(self, value):
		""" do_mag """
		self._do_stars_real(False)
		self._mag = value
		self._scbsc5.max_mag = self._mag
		# turn on stars button
		self.ui.stars_button_set(True)
		self._do_stars_real(True)

	def do_focal_length(self, focal_length_mm):
		""" do_focal_length """
		self.my_camera.camera.reload(focal_length_mm=focal_length_mm)
		# refresh everything
		self.update_starfield_and_more()
		self.draw()

	def do_accelerate(self, value):
		""" do_accelerate """
		self._switch_accelerate_time = value
		# reset line data - otherwise it's messy
		self.plot_starfield_centerline_clear()
		self.draw()
		# reset timer interval
		self.timer_reset()

	# called from UI ...
	def do_stars(self, value):
		""" do_stars """
		self._do_stars_real(value)

	def _do_stars_real(self, value):
		""" do_stars_real """
		self._switch_stars = value
		self._scbsc5.change(self._switch_stars)
		self.draw()

	def do_satellite_selection(self, val):
		""" do_satellite_selection """
		self._satellite_name = val
		self.my_camera.find_tle(self._satellite_name)
		# remove satellite track
		self.plot_starfield_centerline_clear()
		self.plot_earthtrack_dot_clear()
		# refresh everything
		self.update_starfield_and_more()
		self.draw()

	def do_satellite_attitude(self, val):
		""" do_satellite_attitude """
		self._pointing = val
		self.plot_starfield_centerline_clear()
		self.update_starfield_and_more()
		self.draw()

	def do_rpy(self, val, k):
		""" do_rpy """
		self.ui.rpy_values_deg[k] = float(val)
		# refresh everything
		self.update_starfield_and_more()
		self.draw()
		self._cv.update_orientation(
			# XYZ should be r,p,y - but camera is on +Y side - so swap pitch & roll for some reason
			self.ui.rpy_values_deg['roll'],
			self.ui.rpy_values_deg['pitch'],
			self.ui.rpy_values_deg['yaw']
		)

	def do_reset(self):
		""" do_reset """
		# RESET focus
		focal_length_mm = self._DEFAULT_FOCAL_LENGTH
		self.ui.focal_length_buttons_set(focal_length_mm=focal_length_mm)
		self.my_camera.camera.reload(focal_length_mm=focal_length_mm)

		# RESET star magnitude
		self._mag = 5.0
		self._scbsc5.max_mag = self._mag
		self.ui.star_mag_buttons_set(mag=self._mag)

		# RESET accelerate
		self.ui.accelerate_button_set(False)
		self._switch_accelerate_time = False

		# RESET show stars
		self._switch_stars = False
		self.ui.stars_button_set(False)
		self._do_stars_real(False)

		# RESET rpy
		for k in self.ui.rpy_values_deg:
			self.ui.rpy_values_deg[k] = 0.0
			self.ui.v_sliders[k].set(0.0)

		# RESET match
		self._switch_match_stars = False
		self.ui.match_stars_button_set(False)

		# RESET earth
		self.plot_earthtrack_dot_clear()

		# RESET sun, moon, planets
		self._switch_planets_etc = False
		self.ui.planets_etc_button_set(False)
		self._sun_moon_planets.change(self._switch_planets_etc)

		# RESET constellations
		self._switch_constellation_boundaries = False
		self.ui.constellation_boundaries_button_set(False)
		self._constellation_boundaries.change(self._switch_constellation_boundaries)

		# RESET earth vector
		self._switch_earth_vector = False
		self.ui.earth_vector_button_set(False)

		# RESET satellite selection
		self.ui.satellite_selection_set(0)
		self._satellite_name = static_list_satellites[0].name
		self.my_camera.find_tle(self._satellite_name)

		# RESET satelliite attitude
		self._pointing = 'vv'
		self.ui.satellite_attitude_set(0)

		# RESET text boxes
		s = ''
		self.ui.star_found_text(s)
		self.ui.misc_text(s)

		# RESET camera image
		self._ci.reset()

		# Now redraw everything - by reseting the timer.
		self.plot_starfield_centerline_clear()
		# self.update_starfield_and_more()
		# self.draw()
		self._cv.update_orientation(
			self.ui.rpy_values_deg['pitch'],
			self.ui.rpy_values_deg['roll'],
			self.ui.rpy_values_deg['yaw']
		)

		# RESET timer interval
		self.timer_reset()

	def do_camera_select(self, camera_name):
		""" do_camera_select """
		self.my_camera.camera.reload(camera_name)
		# need to resize the camera view area to match new camera sensor
		self._ci.resize(self.my_camera.camera.nx, self.my_camera.camera.ny)
		# refresh everything
		self.update_starfield_and_more()
		self.draw()

		print('do_camera_select(): equiv focal length = %d' % (self.my_camera.camera.equivilant_focal_length))

	def _match_against_bsc5(self):
		""" _match_against_bsc5 """

		# see if we actually match any stars within the view from the camera?
		center_pixel_x = self.my_camera.camera.nx/2
		center_pixel_y = self.my_camera.camera.ny/2
		ra_deg, dec_deg = self.my_camera.pixel_to_radec(center_pixel_x, center_pixel_y)

		# center
		# create a (for now) array of length one to test against
		pixels = {(center_pixel_x, center_pixel_y): (ra_deg, dec_deg)}

		# pixel_list & coords_list need to be in-sync (obviously)
		pixel_list = list(pixels.keys())
		coords_list = list(pixels.values())

		# get into SkyCoords's with ICRS
		coords_list_icrs = SkyCoord(coords_list, unit='deg', frame='icrs')

		# For each image direction, find nearest star in catalog
		idx, sep2d, _ = coords_list_icrs.match_to_catalog_sky(self._scbsc5.skycoords)

		# Return matches with separation info
		matches = []
		for ii in range(len(coords_list_icrs)):
			matches.append({
				'pixel': pixel_list[ii], 'coords': coords_list_icrs[ii],
				'bsc5': self._scbsc5.stars[idx[ii]],
				'star_coord': self._scbsc5.skycoords[idx[ii]],
				'separation_arcsec': sep2d[ii].arcsec,
			})
		return matches

	def timer_reset(self):
		""" timer_reset """
		if self._timer_id is not None:
			self.ui.root.after_cancel(self._timer_id)
			self._timer_id = None
		# reprime
		self.timer_went_off()

	def timer_went_off(self):
		""" timer_went_off """
		self._timer_id = None
		# update the time and recaculate the attitude (based on the new time)
		# and deal with time interval and timers
		if self._switch_accelerate_time is True:
			# accelerate - i.e. jump time ahead quickly - TODO this value should be based on orbital params
			seconds = (60 - self.my_camera.observed_time.datetime.second) + self._TIME_JUMP_ACCELERATE
			self.my_camera.adjust_by_seconds(seconds)
			# hence sleep is half a second
			sleep_length = self._TIMER_SLEEP_ACCELERATE
		else:
			# realtime
			self.my_camera.now()
			# hence sleep is five seconds
			sleep_length = self._TIMER_SLEEP_NORMAL

		# now repaint/update sky
		self.update_starfield_and_more()
		self._constellation_boundaries.change(self._switch_constellation_boundaries)
		self._sun_moon_planets.change(self._switch_planets_etc, self.my_camera.observed_time, self.my_camera.camera.eci_position_vector)
		self.draw()

		# and finally, setup to trigger outselves at the next timer time
		self._timer_id = self.ui.root.after(sleep_length, self.timer_went_off)
