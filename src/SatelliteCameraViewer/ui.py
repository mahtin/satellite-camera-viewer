""" ui.py """

import sys
import platform
import tkinter as tk
from tkinter import ttk, messagebox, TclError

from . import __version__

## # pylint: disable=unnecessary-lambda

class UserInterface:
	""" UserInterface """

	_cam_slider_rpy_text = {
		'roll': 'Roll (X) side-to-side',
		'pitch': 'Pitch (Y) nose-up-down',
		'yaw': 'Yaw((Z) left-right'
	}

	def __init__(self, title=None):
		""" UserInterface """
		self._root = tk.Tk()
		self._set_icon()

		# configure UI gloablly first (presently disabled - as it affects the menu bar)
		# self._root.option_add('*Font', (self.font['family'], self.font['size'] - 2))

		self._style = ttk.Style()
		self._style.configure('Horizontal.TScale', sliderthickness=0, borderwidth=0, sliderlength=0)	# does not work - hence zeros
		self._style.configure('TLabel', justify='left', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TOptionMenu', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TCheckbutton', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TMenubutton', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TRadiobutton', justify='left', font=(self.font['family'], self.font['size']-2, ''))

		self._core = None
		self._title_label = None
		self._camera_info_box = None
		self._star_found_text_box = None
		self._misc_text_box = None

		self._accelerate_button = None
		self._focal_length_buttons = {}
		self._star_mag_buttons = {}
		self._satellite_attitude_buttons ={}
		self._rpy_label = None
		self._sat_label = None
		self._photo_label = None

		self._rpy_sliders = {}

		# rpy_values_deg - values of Roll, Pitch, and Yaw sliders.
		self.rpy_values_deg = {
			'roll': 0.0,		# X
			'pitch': 0.0,		# Y
			'yaw': 0.0		# Z
		}

		if title:
			self.root.title('Satellite Camera Viewer')

	@property
	def root(self):
		""" root """
		return self._root

	@property
	def font(self):
		""" font """
		return tk.font.nametofont("TkDefaultFont").actual()

	@property
	def core(self):
		""" core """
		return self._core

	@core.setter
	def core(self, value=None):
		""" core """
		self._core = value

	def frame(self, parent, borderwidth=1, row=0, col=0, colspan=1, padx=2, pady=2, sticky='nsew', anchor=None):
		""" frame """
		if borderwidth == 0:
			relief = ''
		else:
			relief='solid'
		f = ttk.Frame(parent, borderwidth=borderwidth, relief=relief)
		if anchor is not None:
			f.pack(padx=padx, pady=pady, anchor=anchor)
		else:
			f.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky=sticky)
		return f

	def labelframe(self, parent, text='', borderwidth=1, row=0, col=0, colspan=1, padx=2, pady=2, sticky='nsew'):
		""" labelframe """
		if borderwidth == 0:
			relief = ''
		else:
			relief='solid'
		f = ttk.LabelFrame(parent, text=text, borderwidth=borderwidth, relief=relief)
		f.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky=sticky)
		return f

	# PROGRAM ICON

	def _set_icon(self):
		""" _set_icon """
		# self._root.iconbitmap(default='satellite-camera-viewer.xbm')
		platform_os = platform.system()
		try:
			if platform_os == 'Windows':
				# Windows handles .ico files perfectly via iconbitmap
				self._root.iconbitmap('img/satellite-camera-viewer-icon.ico')
			elif platform_os == 'Darwin':  # macOS
				# Use a PNG or GIF file with iconphoto
				self._root.iconphoto(False, tk.PhotoImage(file='img/satellite-camera-viewer-icon.png'))
			else:
				# Linux / alternative environments
				self._root.iconphoto(True, tk.PhotoImage(file='img/satellite-camera-viewer-icon.png'))
		except TclError as e:
			print('TclError: program icon not loaded:', e, '(low priority - continuing)', file=sys.stderr)

	# MENU BAR etc

	def _show_help_info(self):
		""" _show_help_info - Defines the uniform content for the Help Dialog """
		messagebox.showinfo(
			title='Help Satellite Camera Viewer',
			message='Satellite Camera Viewer\nVersion %s' % (__version__),
			detail='help coming soon',
		)

	def _show_about_info(self):
		""" _show_about_info - Defines the uniform content for the About Dialog """
		messagebox.showinfo(
			title='About Satellite Camera Viewer',
			message='Satellite Camera Viewer\nVersion %s' % (__version__),
			detail='(c) 2026 Martin J Levy\nAll rights reserved\n\n' +
				'https://github.com/mahtin/satellite-camera-viewer\n' +
				'Built with Python, Tkinter, Matplotlib.pyplot, AstroPy, PyVista, ...',
		)

	def menubar(self):
		""" menubar """

		self._menubar = tk.Menu(self.root)

		# File menu ...
		file_menu = tk.Menu(self._menubar, tearoff=0)
		file_menu.add_command(label='New File', command=lambda: print('DEBUG: New File clicked'))
		file_menu.add_command(label='Open', command=lambda: print('DEBUG: Open clicked'))
		file_menu.add_separator()
		file_menu.add_command(label='Exit', command=self.root.quit)
		self._menubar.add_cascade(label='File', menu=file_menu)

		# Help menu ...
		help_menu = tk.Menu(self._menubar, tearoff=0)
		help_menu.add_command(label='Help', command=self._show_help_info)
		help_menu.add_separator()
		help_menu.add_command(label='About', command=self._show_about_info)
		self._menubar.add_cascade(label='Help', menu=help_menu)

		# add the menubar
		self.root.config(menu=self._menubar)

		# special case code for specific os's ... sadly
		if platform.system() == 'Darwin':
			# special case on Mac ... add to apple menu
			self.root.createcommand('tk::mac::ShowAboutBox', self._show_about_info)

	# TITLE

	#def title_label(self, parent, text):
	#	""" title_label """
	#	l = ttk.Label(parent, text=text, justify='left', font=('', 24, 'bold'))
	#	l.pack(padx=2, pady=2)
	#	self._title_label = l

	# INFO TEXT BOXES

	def camera_info_box(self, parent, row, col):
		""" camera_info_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
		self._camera_info_box = t

	def misc_text_box(self, parent, row, col):
		""" misc_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
		self._misc_text_box = t

	def star_found_text_box(self, parent, row, col):
		""" star_found_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
		self._star_found_text_box = t

	def camera_info(self, text):
		""" camera_info """
		self._camera_info_box.config(state='normal')
		self._camera_info_box.delete('1.0', tk.END)
		self._camera_info_box.insert(tk.END, '%s' % (text))
		self._camera_info_box.config(state='disabled')

	def star_found_text(self, text):
		""" star_found_text """
		self._star_found_text_box.config(state='normal')
		self._star_found_text_box.delete('1.0', tk.END)
		self._star_found_text_box.insert(tk.END, '%s' % (text))
		self._star_found_text_box.config(state='disabled')

	def misc_text(self, text):
		""" misc_text """
		self._misc_text_box.config(state='normal')
		self._misc_text_box.delete('1.0', tk.END)
		self._misc_text_box.insert(tk.END, '%s' % (text))
		self._misc_text_box.config(state='disabled')

	# BUTTONS

	def do_accelerate(self, value):
		""" do_accelerate """
		self.core.do_accelerate(bool(value.get()))

	def accelerate_button(self, parent, row, col):
		""" accelerate_button """
		self._accelerate_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Accelerate?', variable=self._accelerate_state, command=lambda value=self._accelerate_state: self.do_accelerate(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._accelerate_button = b

	def accelerate_button_set(self, value):
		""" accelerate_button_set """
		self._accelerate_state.set(bool(value))

	def do_stars(self, value):
		""" do_stars """
		self.core.do_stars(bool(value.get()))

	def stars_button(self, parent, row, col):
		""" stars_button """
		self._stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Stars?', variable=self._stars_state, command=lambda value=self._stars_state: self.do_stars(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._stars_button = b

	def stars_button_set(self, value):
		""" set_stars_button """
		self._stars_state.set(bool(value))

	def do_match_stars(self, value):
		""" do_match_stars """
		self.core.do_match_stars(bool(value.get()))

	def match_stars_button(self, parent, row, col):
		""" match_stars_button """
		self._match_stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Match stars?', variable=self._match_stars_state, command=lambda value=self._match_stars_state: self.do_match_stars(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._match_stars_button = b

	def match_stars_button_set(self, value):
		""" match_stars_button_set """
		self._match_stars_state.set(bool(value))

	def do_planets_etc(self, value):
		""" do_planets_etc """
		self.core.do_planets_etc(bool(value.get()))

	def planets_etc_button(self, parent, row, col):
		""" planets_etc_button """
		self._planets_etc_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Show Planets etc?', variable=self._planets_etc_state, command=lambda value=self._planets_etc_state: self.do_planets_etc(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._planets_etc_button = b

	def planets_etc_button_set(self, value):
		""" planets_etc_button_set """
		self._planets_etc_state.set(bool(value))

	def do_constellation_boundaries(self, value):
		""" do_constellation_boundaries """
		self.core.do_constellation_boundaries(bool(value.get()))

	def constellation_boundaries_button(self, parent, row, col):
		""" constellation_boundaries_button """
		self._constellation_boundaries_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Constellation Boundaries?', variable=self._constellation_boundaries_state, command=lambda value=self._constellation_boundaries_state: self.do_constellation_boundaries(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._constellation_boundaries_button = b

	def constellation_boundaries_button_set(self, value):
		""" constellation_boundaries_button_set """
		self._constellation_boundaries_state.set(bool(value))

	def do_earth_vector(self, value):
		""" do_earth_vector """
		self.core.do_earth_vector(bool(value.get()))

	def earth_vector_button(self, parent, row, col):
		""" earth_vector_button """
		self._earth_vector_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Earth Vector?', variable=self._earth_vector_state, command=lambda value=self._earth_vector_state: self.do_earth_vector(value))
		b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
		self._earth_vector_button = b

	def earth_vector_button_set(self, value):
		""" earth_vector_button_set """
		self._earth_vector_state.set(bool(value))

	# STAR MAGNITUDE

	def do_mag(self, value):
		""" do_mag """
		self.core.do_mag(float(value))

	def star_mag_buttons(self, parent, row, col, mags):
		""" star_mag_buttons """
		lf = self.labelframe(parent, 'Star Magnitude')
		lf.grid(row=row, column=col)
		m_default = mags[2]
		self._star_mag_buttons_variable = tk.DoubleVar(value=m_default)
		for m in mags:
			# radiobutton
			b = ttk.Radiobutton(lf, text='%.1f' % m, variable=self._star_mag_buttons_variable, value=m, command=lambda value=m: self.do_mag(value))
			b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
			self._star_mag_buttons[m] = b
			row += 1

	def star_mag_buttons_set(self, mag=5.0):
		""" star_mag_buttons_set """
		self._star_mag_buttons_variable.set(float(mag))

	# FOCAL LENGTH

	def do_focal_length(self, value):
		""" do_focal_length """
		self.core.do_focal_length(float(value))

	def focal_length_buttons(self, parent, row, col, focal_lengths):
		""" focal_length_buttons """
		lf = self.labelframe(parent, 'Focal Length')
		lf.grid(row=row, column=col)
		f_default = focal_lengths[1]
		self._focal_length_buttons_variable = tk.IntVar(value=f_default)
		for f in focal_lengths:
			# radiobutton
			b = ttk.Radiobutton(lf, text='%d mm' % f, variable=self._focal_length_buttons_variable, value=f, command=lambda value=f: self.do_focal_length(value))
			b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
			self._focal_length_buttons[f] = b
			row += 1

	def focal_length_buttons_set(self, focal_length=50):
		""" focal_length_set """
		self._focal_length_buttons_variable.set(focal_length)

	# SATELLITE SELECTION

	def do_satellite_selection(self, value):
		""" do_satellite_selection """
		self.core.do_satellite_selection(str(value))

	def satellite_selection(self, parent, row, col, satellite_names):
		""" satellite_selection """
		self._satellite_name_default = satellite_names[0]
		self._satellite_selected = tk.StringVar(value=self._satellite_name_default)
		drop = ttk.OptionMenu(parent, self._satellite_selected, self._satellite_name_default, *satellite_names, command=lambda value: self.do_satellite_selection(value))
		drop.grid(row=row, column=col, columnspan=7, padx=2, pady=2, sticky='ew')
		self._satellite_selection_drop = drop

	def satellite_selection_set(self, value=0):
		""" satellite_selection_set """
		# can only do value = 0
		self._satellite_selected.set(self._satellite_name_default)

	# SATELLITE BUTTONS

	def do_satellite_attitude(self, value):
		""" do_satellite_attitude """
		self.core.do_satellite_attitude(str(value))

	def satellite_attitude_buttons(self, parent, row, col, attitude_names):
		""" satellite_attitude_buttons """
		self._attitude_names_default = attitude_names[0]
		self._satellite_attitude_buttons_variable = tk.IntVar(value=self._attitude_names_default)
		for a in attitude_names:
			# radiobutton
			b = ttk.Radiobutton(parent, text=a, variable=self._satellite_attitude_buttons_variable, value=a, command=lambda value=a: self.do_satellite_attitude(value))
			b.grid(row=row, column=col, padx=2, pady=2, sticky='nw')
			self._satellite_attitude_buttons[a] = b
			col += 1

	def satellite_attitude_set(self, value=0):
		""" satellite_attitude_set """
		# can only do value = 0
		self._satellite_attitude_buttons_variable.set(self._attitude_names_default)

	# ROLL PITCH YAW

	def rpy_label(self, parent, text, row, col):
		""" rpy_label """
		rpy_label = 'Roll(X) / Pitch(Y) / Yaw(Z) controls for satellite body (and hence camera)'
		l = ttk.Label(parent, text=rpy_label, wraplength=160)
		l.grid(row=row, column=col, padx=2, pady=2, sticky='w')
		self._rpy_label = l

	def do_rpy(self, val, k):
		""" do_rpy """
		self.core.do_rpy(float(val), k)

	def rpy_sliders(self, parent, row, col):
		""" rpy_sliders """
		lf = self.labelframe(parent, 'Attitude')
		lf.grid(row=row, column=col, sticky='ew')
		self.v_sliders = {}
		max_width = max(len(k) for v,k in self._cam_slider_rpy_text.items())
		for k,v in self.rpy_values_deg.items():
			l = ttk.Label(lf, text=self._cam_slider_rpy_text[k], width=max_width+5)
			l.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
			row += 1
			self.v_sliders[k] = tk.IntVar(value=int(v))
			s = ttk.Scale(lf,
				# label=self._cam_slider_rpy_text[k],
				variable=self.v_sliders[k],
				from_=-90, to=90,
				# resolution=10.0,
				# showvalue=True,
				orient='horizontal',
				command=lambda value,k=k: self.do_rpy(value, k))
			s.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
			self._rpy_sliders[k] = s
			row += 1

	# 3D cubesat image

	def sat_label(self, parent, row, col, width=300, height=300):
		""" sat_label """
		l = tk.Label(parent, bg='whitesmoke', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=2, pady=2, sticky='w')
		self._sat_label = l
		return self._sat_label

	# photo image

	def photo_label(self, parent, row, col, width=300, height=300):
		""" photo_label """
		l = tk.Label(parent, bg='cyan', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=2, pady=2, sticky='w')
		self._photo_label = l
		# self._image150x150(width, height)
		return self._photo_label

	# RESET BUTTON

	def do_reset(self):
		""" do_reset """
		self.core.do_reset()

	def reset_everything_button(self, parent, row, col):
		""" reset_everything_button """
		self._style.configure('Reset.TButton',
			foreground='lightcoral',
			font=(self.font['family'], self.font['size'], 'bold'),
		)
		b = ttk.Button(parent, text='RESET EVERYTHING', style='Reset.TButton', command=self.do_reset)
		b.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
		self._reset_everything_button = b

	def mainloop(self):
		""" mainloop """
		self.root.mainloop()
