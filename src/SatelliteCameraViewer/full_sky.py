""" camera_display.py """

import math
import warnings

import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from astropy.coordinates import SkyCoord

from .SatelliteCamera import SatelliteCamera, SatelliteCameraError
from .BSC5Stars import BSC5Stars
from .NikonD5Camera import NikonD5Camera
from .DoCameraImage import DoCameraImage
from .DoCubesatViewer import DoCubesatViewer

from .misc import arcseconds_to_radians, ra_fix, mag_map, split_plot_mollweide_line_ra_dec_deg, split_plot_mollweide_line
from .ecliptic import ecliptic, body, galactic_plane, moon_illumination
from .constellation_database import ConstellationDatabase
from .stars_in_polygon_icrs import stars_in_polygon_icrs

#
# Do this to debug:
# .../matplotlib/projections/geo.py:397: RuntimeWarning: invalid value encountered in arcsin
# theta = np.arcsin(y / np.sqrt(2))

# Turn all RuntimeWarnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

class UserInterface:
	""" UserInterface """

	_full_sky = None
	_title_label = None
	_camera_info_box = None
	_star_found_text_box = None
	_misc_text_box = None
	_realtime_button = None
	_focal_length_buttons = {}
	_star_mag_buttons = {}
	_rpy_label = None
	_sat_label = None
	_photo_label = None
	_rpy_sliders = {}

	rpy_values_deg = {
		'roll': 0.0,
		'pitch': 0.0,
		'yaw': 0.0
	}

	_cam_slider_rpy_text = {
		'roll': 'Roll (X) side-to-side',
		'pitch': 'Pitch (Y) nose-up-down',
		'yaw': 'Yaw((Z) left-right'
	}

	@classmethod
	def register_full_sky(cls, f):
		""" register_full_sky """
		cls._full_sky = f

	# TITLE

	@classmethod
	def title_label(cls, parent, text):
		""" title_label """
		l = ttk.Label(parent, text=text, justify='left', font=('', 24, 'bold'))
		l.pack(padx=5, pady=2)
		cls._title_label = l

	# INFO TEXT BOXES

	@classmethod
	def camera_info_box(cls, parent, row, col):
		""" camera_info_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		cls._camera_info_box = t

	@classmethod
	def misc_text_box(cls, parent, row, col):
		""" misc_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		cls._misc_text_box = t

	@classmethod
	def star_found_text_box(cls, parent, row, col):
		""" star_found_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		cls._star_found_text_box = t

	@classmethod
	def camera_info(cls, text):
		""" camera_info """
		cls._camera_info_box.config(state='normal')
		cls._camera_info_box.delete('1.0', tk.END)
		cls._camera_info_box.insert(tk.END, '%s' % (text))
		cls._camera_info_box.config(state='disabled')

	@classmethod
	def star_found_text(cls, text):
		""" star_found_text """
		cls._star_found_text_box.config(state='normal')
		cls._star_found_text_box.delete('1.0', tk.END)
		cls._star_found_text_box.insert(tk.END, '%s' % (text))
		cls._star_found_text_box.config(state='disabled')

	@classmethod
	def misc_text(cls, text):
		""" misc_text """
		cls._misc_text_box.config(state='normal')
		cls._misc_text_box.delete('1.0', tk.END)
		cls._misc_text_box.insert(tk.END, '%s' % (text))
		cls._misc_text_box.config(state='disabled')

	# BUTTONS

	@classmethod
	def do_realtime(cls, value):
		""" do_realtime """
		cls._full_sky.do_realtime(value)

	@classmethod
	def realtime_button(cls, parent, row, col):
		""" realtime_button """
		cls._realtime_state = tk.BooleanVar()
		b = ttk.Checkbutton(parent, text="Accelerate?", variable=cls._realtime_state, command=lambda value=cls._realtime_state: cls.do_realtime(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky="nw")
		cls._realtime_button = b

	@classmethod
	def realtime_button_set(cls, value):
		""" realtime_button_set """
		cls._realtime_state.set(value)

	@classmethod
	def do_stars(cls, value):
		""" do_stars """
		cls._full_sky.do_stars(value)

	@classmethod
	def stars_button(cls, parent, row, col):
		""" stars_button """
		cls._stars_state = tk.BooleanVar()
		b = ttk.Checkbutton(parent, text="Stars?", variable=cls._stars_state, command=lambda value=cls._stars_state: cls.do_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky="nw")
		cls._stars_button = b

	@classmethod
	def stars_button_set(cls, value):
		""" set_stars_button """
		cls._stars_state.set(value)

	@classmethod
	def do_match_stars(cls, value):
		""" do_match_stars """
		cls._full_sky.do_match_stars(value)

	@classmethod
	def match_stars_button(cls, parent, row, col):
		""" match_stars_button """
		cls._match_stars_state = tk.BooleanVar()
		b = ttk.Checkbutton(parent, text="Match stars?", variable=cls._match_stars_state, command=lambda value=cls._match_stars_state: cls.do_match_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky="nw")
		cls._match_stars_button = b

	@classmethod
	def match_stars_button_set(cls, value):
		cls._match_stars_state.set(value)

	# STAR MAGNITUDE

	@classmethod
	def do_mag(cls, value):
		""" do_mag """
		cls._full_sky.do_mag(value)

	@classmethod
	def star_mag_buttons(cls, parent, row, col, mags):
		""" star_mag_buttons """
		l = ttk.Label(parent, text='Star Magnitude', justify='left')
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		row += 1
		m_default = mags[2]
		cls._star_mag_buttons_variable = tk.DoubleVar(value=m_default)
		for m in mags:
			# radiobutton
			b = tk.Radiobutton(parent, text='%.1f' % m, variable=cls._star_mag_buttons_variable, justify='left', value=m, command=lambda value=m: cls.do_mag(value))
			b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
			cls._star_mag_buttons[m] = b
			row += 1

	@classmethod
	def star_mag_buttons_set(cls, mag=5.0):
		""" star_mag_buttons_set """
		cls._star_mag_buttons_variable.set(mag)

	# FOCAL LENGTH

	@classmethod
	def do_focal_length(cls, f):
		""" do_focal_length """
		cls._full_sky.do_focal_length(f)

	@classmethod
	def focal_length_buttons(cls, parent, row, col, focal_lengths):
		""" focal_length_buttons """
		l = ttk.Label(parent, text='Focal Length', justify='left')
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		row += 1
		f_default = focal_lengths[1]
		cls._focal_length_buttons_variable = tk.IntVar(value=f_default)
		for f in focal_lengths:
			# radiobutton
			b = tk.Radiobutton(parent, text='%d mm' % f, variable=cls._focal_length_buttons_variable, justify='left', value=f, command=lambda f=f: cls.do_focal_length(f))
			b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
			cls._focal_length_buttons[f] = b
			row += 1

	@classmethod
	def focal_length_buttons_set(cls, focal_length=50):
		""" focal_length_set """
		cls._focal_length_buttons_variable.set(focal_length)

	# ROLL PITCH YAW

	@classmethod
	def rpy_label(cls, parent, text, row, col):
		""" rpy_label """
		l = ttk.Label(parent, text=text, justify='left', wraplength=160)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		cls._rpy_label = l

	@classmethod
	def do_rpy(cls, val, k):
		""" do_rpy """
		cls._full_sky.do_rpy(val, k)

	@classmethod
	def rpy_sliders(cls, parent, row, col):
		""" rpy_sliders """
		cls.v_sliders = {}
		for k,v in cls.rpy_values_deg.items():
			cls.v_sliders[k] = tk.IntVar(value=int(v))
			s = tk.Scale(parent, label=cls._cam_slider_rpy_text[k], variable=cls.v_sliders[k], from_=-90, to=90, resolution=10.0, showvalue=True,
				orient='horizontal', command=lambda val,k=k: cls.do_rpy(val, k))
			s.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
			cls._rpy_sliders[k] = s
			row += 1

	# 3D cubesat image

	@classmethod
	def sat_label(cls, parent, row, col, width=300, height=300):
		""" sat_label """
		l = tk.Label(parent, bg='whitesmoke', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		cls._sat_label = l
		return cls._sat_label

	# photo image

	@classmethod
	def photo_label(cls, parent, row, col, width=300, height=300):
		""" photo_label """
		l = tk.Label(parent, bg='cyan', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		cls._photo_label = l
		# cls._image150x150(width, height)
		return cls._photo_label

	# RESET BUTTON

	@classmethod
	def do_reset(cls):
		""" do_reset """
		cls._full_sky.do_reset()

	@classmethod
	def reset_everyting_button(cls, parent, row, col):
		""" eeset_everyting_button """
		font = tk.font.nametofont("TkDefaultFont").actual()
		style = ttk.Style()
		style.configure('Reset.TButton',
			foreground=FullSky.COLORS['reset-color'],
			font=(font['family'], font['size'], 'bold'),
		)
		b = ttk.Button(parent, text='RESET EVERYTHING', style='Reset.TButton', command=lambda: cls.do_reset())
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		cls._reset_everything_button = b

class FullSky:
	""" FullSky """

	# https://matplotlib.org/stable/gallery/color/named_colors.html#css-colors
	COLORS = {
		'fig-facecolor': '#ebebeb',
		'sky-facecolor': 'whitesmoke',
		'sky-grid': 'lightgrey',
		'sky-axis': 'dimgrey',
		'sky-label': 'black',
		'sky-ecliptic': 'dimgrey',
		'sky-galactic': 'saddlebrown',
		'reset-color': 'lightcoral',
		'reset-text': 'cornsilk',
		'plot-center': 'darkgreen',
		'plot-corners': 'darkblue',
		'plot-polygon': 'orange',
		'plot-hull': 'orange',
		'plot-pixels': 'cornflowerblue',
		'plot-pixels-corner': 'royalblue',
		'stars': 'black',
		'stars-found': 'magenta',
		'constellations': 'red',
		'sun': 'darkorange',
		'moon': 'dimgrey',
		'match': 'red',
	}

	_verbose = False

	_switch_accelerate_time = False
	_switch_match_stars = False

	def __init__(self, root=None, font_family='san-serif', font_size=10):
		""" FullSky """
		if root is None:
			raise ValueError('FullSky() needs root value')
		self._root = root

		self._font_family = font_family
		self._font_size = font_size

		self._create_subplot()
		self._paint_axis()

		self._nikon = NikonD5Camera()

		self._canvas = None

		self.plot_ecliptic()
		self.plot_sun_moon()
		if False:
			# not needed presently becaused the number of stars plotted is so low
			self.plot_galactic_plane()

		self._items_plotted = []
		self._center_line_plot = None
		self._center_line_data = None

		self._stars_plot = None

		mag = 5.0
		self._scbsc5 = StarsConstellationsBSC5(mag)

	def cubesat_viewer_register(self, u=3, label=None, w=400, h=300):
		""" cubesat_viewer_register """
		self._cv = DoCubesatViewer(u=u, label=label, w=w, h=h)

	def camera_image_register(self, label=None, nx=400, ny=300, w=400, h=300):
		""" camera_image_register """
		self._ci = DoCameraImage(label=label, nx=nx, ny=ny, w=w, h=h)

	def _create_subplot(self):
		""" _create_subplot """
		# plt.style.use('classic')
		# plt.rcParams['toolbar'] = 'None'	# was 'toolbar2' but we don't need the controls
		self._fig = Figure(figsize=(16.0, 8.0), dpi=65, layout='tight')
		self._fig.patch.set_linewidth(0)
		self._fig.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
		self._fig.set_layout_engine(layout='tight')
		self._fig.patch.set_facecolor(FullSky.COLORS['fig-facecolor'])
		# projection='mollweide' is an equal-area, pseudocylindrical projection where parallels are straight lines.
		self._ax = self._fig.add_subplot(1, 1, 1, projection='mollweide')
		self._ax.set_facecolor(FullSky.COLORS['sky-facecolor'])

	def _paint_axis(self):
		""" _paint_axis """
		# grid lines
		self._ax.grid(color=FullSky.COLORS['sky-grid'], alpha=0.5)
		# x axis (ra)
		# 24 hours is 360 degrees - one hour is 15 degrees. Mark every other hour (i.e 30 degrees)
		# note that this projection is -180 to +180 - we need to handle that later on - for now we simply change the lables
		# When dealing with astronomical coordinates the right ascension increases eastward, located conventionally left on celestial charts.
		x_values = [math.radians(v) for v in range(-180,180+30,30)]
		x_labels = ['', '10h','8h','6h','4h','2h','0h','22h','20h','18h','16h','14h', '']
		self._ax.set_xticks(x_values, x_labels, rotation='vertical', color=FullSky.COLORS['sky-axis'], alpha=0.5,
			fontdict={'fontsize':self._font_size, 'horizontalalignment':'center', 'verticalalignment':'center'}
		)
		self._ax.set_xlabel('Right Ascension (hours)', color=FullSky.COLORS['sky-label'],
			fontdict={'fontsize':self._font_size, 'horizontalalignment':'center', 'verticalalignment':'top'}
		)

		# y axis (dec)
		y_values = [math.radians(v) for v in range(-90,90+10,10)]
		y_labels = [str(v) for v in range(-90,90+10,10)]
		# remove 90 and 80 and -80 and -90 (as they don't draw correctly - and aren't needed)
		for ii in [0, 1, -1, -2]:
			y_labels[ii] = ''
		self._ax.set_yticks(y_values, y_labels, color=FullSky.COLORS['sky-axis'],
			fontdict={'fontsize':self._font_size, 'horizontalalignment':'center', 'verticalalignment':'center'}
		)
		self._ax.set_ylabel('Declination (degrees)', color=FullSky.COLORS['sky-label'],
			fontdict={'fontsize':self._font_size, 'horizontalalignment':'right', 'verticalalignment':'center'}
		)

	def register_canvas(self, canvas):
		""" register_canvas """
		self._canvas = canvas

	def update_full_sky(self):
		""" update_full_sky """
		# Key Details for Mollweide Projection in Matplotlib:
		# Input Data Formats: Data must be in radians, not degrees, for proper positioning
		# X-Axis (Longitude): Ranges from -PI to +PI
		# Y-Axis (Latitude): Ranges from -PI/2 to +PI/2
		# Plotting with longitude (x) and latitude (y) in radians
		# plt.plot(lon_in_radians, lat_in_radians)

		# clean up from previous run
		self.items_plotted_clear()
		# center
		self.plot_center_data()
		self.plot_center()
		# adjust camera/satellite attitude
		self.nikon.camera.choose_attitude(
			'vv',
			cam_yaw_deg=UserInterface.rpy_values_deg['roll'],
			cam_pitch_deg=UserInterface.rpy_values_deg['pitch'],
			cam_roll_deg=UserInterface.rpy_values_deg['yaw']
		)
		#self.nikon.camera.choose_attitude('star', star_ra_deg=100, star_dec_deg=70)
		#self.nikon.camera.choose_attitude('nadir')
		#self.nikon.camera.choose_attitude('ground', earth_lat_deg=36.974117, earth_lon_deg=-122.030792)

		# border
		p = self.plot_border_vectors()
		self.items_plotted_add(p)

		# camera view /box/polygon
		show_box = False
		show_poly = False
		if show_box:
			# A box does not show edges correctly
			p = self.plot_corners()
			self.items_plotted_add(p)
		if show_poly:
			# Four dots in the corners
			p = self.plot_polygons()
			self.items_plotted_add(p)

		# another view
		if False:
			p = self.plot_hull()
			self.items_plotted_add(p)

		# matrix of pixels (at points)
		p = self.plot_pixels(nsteps=1)
		self.items_plotted_add(p)

		if self._switch_match_stars:
			p = self.plot_matched_stars()
			if p:
				self.items_plotted_add(p)

		# build return string - showing camera info
		angular_width, angular_height, solid_angle_steradians = self.nikon.camera_fov_angular_width_height()

		s = '%s\n%s' % (self.nikon.obs_time.strftime('%Y-%m-%d %H:%M:%S %Z'), str(self.nikon.camera))
		s += '\n%.1f deg width by %.1f deg height |' % (angular_width, angular_height)
		s += ' %.1f%% of whole sky' % (100.0*solid_angle_steradians/(4*math.pi))
		return s

	_sun = None
	_moon = None

	def plot_sun_moon(self):
		""" plot_sun_moon """
		fraction = moon_illumination(self.nikon.obs_time)
		moon_ra_rad, moon_dec_rad = body('moon', self.nikon.obs_time)
		moon_ra_rad = ra_fix([moon_ra_rad])[0]
		if self._moon:
			self._moon.set_offsets([[moon_ra_rad, moon_dec_rad]])
		else:
			self._moon = self._ax.scatter([moon_ra_rad], [moon_dec_rad], color=FullSky.COLORS['moon'], alpha=1.0, s=50.0)

		sun_ra_rad, sun_dec_rad = body('sun', self.nikon.obs_time)
		sun_ra_rad = ra_fix([sun_ra_rad])[0]
		# sun diameter is 0.533 degrees
		if self._sun:
			self._sun.set_offsets([[sun_ra_rad, sun_dec_rad]])
		else:
			self._sun = self._ax.scatter([sun_ra_rad], [sun_dec_rad], color=FullSky.COLORS['sun'], alpha=1.0, s=300.0)

	def plot_galactic_plane(self):
		""" plot_galactic_plane """
		ra_dec_rad = galactic_plane()
		segments = split_plot_mollweide_line(ra_dec_rad[0], ra_dec_rad[1], is_radians=True)
		for ra_rad, dec_rad in segments:
			ra_rad = ra_fix(ra_rad)
			self._ax.plot(ra_rad, dec_rad, label='Galactic Plane', alpha=0.2, color=FullSky.COLORS['sky-galactic'], linewidth=30.0) #, linestyle='dashed')

	def plot_ecliptic(self):
		""" plot_ecliptic """
		ra_dec_rad = ecliptic()
		segments = split_plot_mollweide_line(ra_dec_rad[0], ra_dec_rad[1], is_radians=True)
		for ra_rad, dec_rad in segments:
			ra_rad = ra_fix(ra_rad)
			self._ax.plot(ra_rad, dec_rad, label='Ecliptic Plane', alpha=0.75, color=FullSky.COLORS['sky-ecliptic'], linewidth=0.75, linestyle='dotted')

	def plot_stars(self):
		""" plot_stars """
		# BSC5 stars
		stars_ra_rad, stars_dec_rad, stars_mag = self._scbsc5.get_stars()
		stars_ra_rad = ra_fix(stars_ra_rad)
		stars_size_pixels = mag_map(stars_mag)

		const_ra_rad, const_dec_rad, const_mag = self._scbsc5.get_constellations()
		const_ra_rad = ra_fix(const_ra_rad)
		const_size_pixels = mag_map(const_mag)

		p1 = self._ax.scatter(stars_ra_rad, stars_dec_rad, s=stars_size_pixels, alpha=1, color=FullSky.COLORS['stars'], zorder=5)
		p2 = self._ax.scatter(const_ra_rad, const_dec_rad, s=const_size_pixels, alpha=1, color=FullSky.COLORS['constellations'], zorder=5)
		return p1, p2

	def draw(self):
		""" draw """
		self._canvas.draw()

	@property
	def nikon(self):
		""" nikon """
		return self._nikon

	@property
	def fig(self):
		""" fig """
		return self._fig

	@property
	def ax(self):
		""" ax """
		return self._ax

	@property
	def root(self):
		""" root """
		return self._root

	@property
	def canvas(self):
		""" canvas """
		return self._canvas


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

	def plot_center_data(self):
		""" plot_center_data """
		ra_deg, dec_deg = self.nikon.pixel_to_radec(self.nikon.camera.nx/2, self.nikon.camera.ny/2)
		ra_rad = math.radians(ra_deg)
		dec_rad = np.array([math.radians(dec_deg)])
		ra_rad = ra_fix(np.array([ra_rad]))
		new_data = np.array([np.array([ra_rad[0], dec_rad[0]])])
		if self._center_line_data is None:
			self._center_line_data = new_data
		else:
			self._center_line_data = np.append(self._center_line_data, new_data, axis=0)

	# we keep this one on the screen - so processed differently
	def plot_center(self):
		""" plot_center """
		if self._center_line_plot is None:
			# this is an empty plot
			p = self._ax.plot([], [], color=FullSky.COLORS['plot-center'], alpha=1.0, linewidth=1.5, zorder=10)
			self._center_line_plot = p
		if self._center_line_data is None:
			return
		# trim data (43 is a random number)
		self._center_line_data = self._center_line_data[-43:]

		if isinstance(self._center_line_plot, PathCollection):
			self._center_line_plot.set_offsets(self._center_line_data)
		else:
			# print('center_line_data =', np.degrees(self._center_line_data))
			# self._center_line_plot[0].set_data(self._center_line_data[:, 0], self._center_line_data[:, 1])
			segments = split_plot_mollweide_line(np.degrees(self._center_line_data[:, 0]), np.degrees(self._center_line_data[:, 1]))
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
			self._center_line_plot[0].set_data(all_ra_rad, all_dec_rad)

	def plot_center_clear(self):
		""" plot_center_clear """
		self._center_line_data = None


	def plot_corners(self):
		""" plot_corners """
		box, _ = self.nikon.camera_fov_radec_box()
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
		p = self._ax.plot(ra_rad, dec_rad, color=FullSky.COLORS['plot-corners'], alpha=0.25, linewidth=3.0, linestyle='dashed')
		return p

	def plot_polygons(self):
		""" plot_polygons """
		_, polygon = self.nikon.camera_fov_radec_box()
		ra_rad = [math.radians(float(v)) for v in polygon[0]]
		dec_rad = [math.radians(float(v)) for v in polygon[1]]
		ra_rad = ra_fix(ra_rad)
		p = self._ax.scatter(ra_rad, dec_rad, color=FullSky.COLORS['plot-polygon'], alpha=0.5, s=40.0)
		return p

	def plot_hull(self):
		""" plot_hull """
		hull_coords, _ = self.nikon.camera_fov_convex_hull()
		ra_rad = [math.radians(float(v)) for v in hull_coords[0]]
		dec_rad = [math.radians(float(v)) for v in hull_coords[1]]
		ra_rad = ra_fix(ra_rad)
		# not fixed for wrap yet
		p = self._ax.plot(ra_rad, dec_rad, color=FullSky.COLORS['plot-hull'], alpha=0.15, linewidth=2.0, linestyle='solid')
		return p

	def plot_pixels(self, nsteps=3):
		""" plot_pixels """
		pixels = self.nikon.sensor_to_radec(nsteps=nsteps)
		ra_rad = [math.radians(v[0]) for v in pixels.values()]
		dec_rad = [math.radians(v[1]) for v in pixels.values()]
		ra_rad = ra_fix(ra_rad)
		# all points
		p3 = self._ax.scatter(ra_rad, dec_rad, color=FullSky.COLORS['plot-pixels'], alpha=0.75, s=20.0)
		# learing left point/corner
		p1 = self._ax.scatter(ra_rad[nsteps:nsteps+1], dec_rad[nsteps:nsteps+1], color=FullSky.COLORS['plot-pixels-corner'], alpha=1.0, s=100.0)
		# learing right point/corner
		p2 = self._ax.scatter(ra_rad[-1:], dec_rad[-1], color=FullSky.COLORS['plot-pixels-corner'], alpha=1.0, s=100.0)
		return [p1,p2,p3]

	def plot_border_vectors(self):
		""" plot_border_vectors """
		border_vectors = self.nikon.camera_fov_border_vectors()

		plots = []
		for ra_rad, dec_rad in split_plot_mollweide_line_ra_dec_deg(border_vectors):
			ra_rad = ra_fix(ra_rad)
			p = self._ax.plot(ra_rad, dec_rad, color='red', alpha=1.0, linewidth=1.5, linestyle='solid')
			plots.append(p)
		return plots

	def _match_stars_in_polygon(self):
		""" match_stars_in_polygon """

		border_vectors = self.nikon.camera_fov_border_vectors(border_step=10)
		# look for stars ...
		inside_mask = stars_in_polygon_icrs(self._scbsc5.skycoords, border_vectors)
		found_stars = self._scbsc5.skycoords[inside_mask]
		return found_stars, inside_mask

	def plot_matched_stars(self):
		""" plot_matched_stars """
		# now find all stars inside camara view ...
		found_stars, inside_mask = self._match_stars_in_polygon()
		if len(found_stars) == 0:
			return None

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
					px, py = self.nikon.radec_to_pixel(ra_deg, dec_deg)
				except SatelliteCameraError as e:
					# outside the view of the camera - should not happen if polygon is accurate
					continue
				xy_list.append((px,py))
			if len(found_stars) != len(xy_list):
				print('build_xy_list():', len(found_stars), '!=', len(xy_list))
			return xy_list

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

		self._ci.stars(xy_list=build_xy_list(found_stars), mag_list=stars_mag)
		#self._ci.outline()

		s = 'Camera image has %d stars' % len(found_stars)
		s += '\nMagnitude: ' + build_mag_bucket_list(stars_mag)
		UserInterface.misc_text(s)

		stars_ra_rad = ra_fix(stars_ra_rad)
		stars_size_pixels = mag_map(stars_mag)
		# plot
		p1 = self._ax.scatter(stars_ra_rad, stars_dec_rad, s=stars_size_pixels, alpha=1, color=FullSky.COLORS['stars-found'], zorder=5)
		return p1

	def do_match_stars(self, value):
		""" do_match_stars """
		match_stars_show = value.get()
		self._switch_match_stars = match_stars_show
		if match_stars_show:
			# also show stars if not showing
			self._do_stars_real(False)
			UserInterface.stars_button_set(True)
			self._do_stars_real(True)

	def do_mag(self, value):
		""" do_mag """
		self._do_stars_real(False)
		self._scbsc5.max_mag = value
		# turn on stars button
		UserInterface.stars_button_set(True)
		self._do_stars_real(True)

	def do_focal_length(self, focal_length):
		""" do_focal_length """
		self.nikon.camera.reload(focal_length_mm=float(focal_length))

		# refresh everything
		s = self.update_full_sky()
		self.draw()
		UserInterface.camera_info(s)

	def do_realtime(self, value):
		""" do_realtime """
		self._switch_accelerate_time = value.get()
		# reset line data - otherwise it's messy
		self.plot_center_clear()
		self.draw()

	def do_stars(self, value):
		""" do_stars """
		self._do_stars_real(value.get())

	def _do_stars_real(self, value):
		""" do_stars_real """
		self.do_stars_clear()
		if value:
			# show stars
			self._stars_plot = self.plot_stars()
		self.draw()

	def do_stars_clear(self):
		""" do_stars_clear """
		if self._stars_plot is not None:
			for p in self._stars_plot:
				p.remove()
			self._stars_plot = None

	def do_rpy(self, val, k):
		""" do_rpy """
		UserInterface.rpy_values_deg[k] = float(val)
		# refresh everything
		s = self.update_full_sky()
		self.draw()
		UserInterface.camera_info(s)
		self._cv.update_orientation(
			UserInterface.rpy_values_deg['pitch'],
			UserInterface.rpy_values_deg['roll'],
			UserInterface.rpy_values_deg['yaw']
		)

	def do_reset(self):
		""" do_reset """
		# RESET focus
		focal_length = 50
		UserInterface.focal_length_buttons_set(focal_length=focal_length)
		self.nikon.camera.reload(focal_length_mm=float(focal_length))

		# RESET star magnitude
		mag = 5.0
		UserInterface.star_mag_buttons_set(mag=mag)
		self._scbsc5.max_mag = mag

		# RESET accelerate
		UserInterface.realtime_button_set(False)
		self._switch_accelerate_time = False

		# RESET show stars
		self.do_stars_clear()
		UserInterface.stars_button_set(False)

		# RESET rpy
		for k in UserInterface.rpy_values_deg:
			UserInterface.rpy_values_deg[k] = 0.0
			UserInterface.v_sliders[k].set(0.0)

		# RESET match
		self._switch_match_stars = False
		UserInterface.match_stars_button_set(False)
		s = ''
		UserInterface.star_found_text(s)
		UserInterface.misc_text(s)

		# RESET camera image
		self._ci.reset()

		# Now redraw everything
		self.plot_center_clear()
		s = self.update_full_sky()
		self.draw()
		UserInterface.camera_info(s)
		self._cv.update_orientation(
			UserInterface.rpy_values_deg['pitch'],
			UserInterface.rpy_values_deg['roll'],
			UserInterface.rpy_values_deg['yaw']
		)

	def _match_against_bsc5(self):
		""" _match_against_bsc5 """

		# see if we actually match any stars within the view from the camera?
		center_pixel_x = self.nikon.camera.nx/2
		center_pixel_y = self.nikon.camera.ny/2
		ra_deg, dec_deg = self.nikon.pixel_to_radec(center_pixel_x, center_pixel_y)

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

	def timer_went_off(self):
		""" timer_went_off """
		# update the time and recaculate the attitude (based on the new time)
		if self._switch_accelerate_time is True:
			# jump time ahead quickly
			self.nikon.adjust_by_seconds(120)
		else:
			# realtime
			self.nikon.now()

		# updated sky
		s = self.update_full_sky()
		self.plot_sun_moon()	# sun and moon move when time changes (slightly)
		self.draw()
		# update text
		UserInterface.camera_info(s)

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

			ra_rad.append(center_ra_rad)
			dec_rad.append(center_dec_rad)
			ra_rad.append(star_ra_rad)
			dec_rad.append(star_dec_rad)
			# TODO - only one for now
			break

		UserInterface.star_found_text(s)

		# XXX TODO powered down for now - does not unpaint itself (yet)
		#if self._switch_match_stars:
		#	star = matches[0]['bsc5']
		#	diameter = mag_map(star.mag, multiplier=4.0)
		#	ra_rad = ra_fix(ra_rad)
		#	_star = self._ax.plot(ra_rad, dec_rad, label='Star match', alpha=1.0, color=FullSky.COLORS['match'], linewidth=3.0)
		#	_star = self._ax.scatter(ra_rad[-1:], dec_rad[-1:], facecolors='none', edgecolors=FullSky.COLORS['match'], s=diameter)
		#	_star = self._ax.scatter(ra_rad[0:1], dec_rad[0:1], facecolors=FullSky.COLORS['plot-center'], edgecolors=FullSky.COLORS['plot-center'], s=60)

		# deal with time interval and timers

		if self._switch_accelerate_time is True:
			# half a second
			timer_step = 500
		else:
			# five seconds
			timer_step = 5 * 1000

		# trigger the next timer
		self.root.after(timer_step, lambda: self.timer_went_off())
		self.draw()

class StarsConstellationsBSC5:
	""" StarsConstellationsBSC5 """

	def __init__(self, mag=5.0):
		""" StarsConstellationsBSC5 """
		self._bsc5 = BSC5Stars(max_mag=mag)

		# self.stars = self._bsc5.stars
		# self.skycoords = self._bsc5.skycoords

	@property
	def stars(self):
		""" stars """
		return self._bsc5.stars

	@property
	def skycoords(self):
		""" skycoords """
		return self._bsc5.skycoords

	@property
	def max_mag(self):
		""" max_mag """
		return self._bsc5.max_mag

	@max_mag.setter
	def max_mag(self, value):
		""" max_mag """
		self._bsc5.max_mag = value

	def get_stars(self):
		""" stars """
		stars_ra_rad, stars_dec_rad, stars_mag = self._bsc5.get_stars()
		return stars_ra_rad, stars_dec_rad, stars_mag

	def get_constellations(self, constellations=['Orion', 'Leo']):
		""" constellations """
		const_ra_rad, const_dec_rad, const_mag = self._bsc5.get_constellations(constellations=constellations)
		return const_ra_rad, const_dec_rad, const_mag

