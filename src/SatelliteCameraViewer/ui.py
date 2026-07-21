""" ui.py """

import sys
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
		# this is a very low-level call that's not well documented in the Python code; but is here ...https://www.tcl-lang.org/man/tcl/TkCmd/tk.html
		self._window_system = self.root.tk.call('tk', 'windowingsystem')	# returns x11, win32 or aqua
		# self.root.protocol('WM_DELETE_WINDOW', self._on_closing)
		self._set_icon()
		# this is the basics of an OS independent menu bar
		self._set_menubar_and_keyboard()
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
		return tk.font.nametofont('TkDefaultFont').actual()

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
		try:
			if self._window_system == 'win32':
				# Windows handles .ico files perfectly via iconbitmap
				self._root.iconbitmap('img/satellite-camera-viewer-icon.ico')
			elif self._window_system == 'aqua':  # macOS
				# Use a PNG or GIF file with iconphoto
				self._root.iconphoto(False, tk.PhotoImage(file='img/satellite-camera-viewer-icon.png'))
			else:
				# Linux / alternative environments
				self._root.iconphoto(True, tk.PhotoImage(file='img/satellite-camera-viewer-icon.png'))
		except TclError as e:
			print('TclError: program icon not loaded:', e, '(low priority - continuing)', file=sys.stderr)

	# MENU BAR etc

	def _show_help_info(self, event=None):
		""" _show_help_info - Defines the uniform content for the Help Dialog """
		messagebox.showinfo(
			title='Help Satellite Camera Viewer',
			message='Satellite Camera Viewer\nVersion %s' % (__version__),
			detail='help coming soon',
		)

	def _show_about_info(self, event=None):
		""" _show_about_info - Defines the uniform content for the About Dialog """
		messagebox.showinfo(
			title='About Satellite Camera Viewer',
			message='Satellite Camera Viewer\nVersion %s' % (__version__),
			detail='(c) 2026 Martin J Levy\nAll rights reserved\n\n' +
				'https://github.com/mahtin/satellite-camera-viewer\n' +
				'Built with Python, Tkinter, Matplotlib.pyplot, AstroPy, PyVista, ...',
		)

	def _menu_new_file(self, event=None):
		""" _menu_new_file """
		print('DEBUG: New File clicked', event)

	def _menu_open_file(self, event=None):
		""" _menu_open_file """
		print('DEBUG: Open File clicked', event)

	def _menu_save_file(self, event=None):
		""" _menu_save_file """
		print('DEBUG: Save File clicked', event)

	def _window_close(self, event=None):
		""" _window_close """
		print('DEBUG: Window Close clicked', event)
		# we only have one window - so it's a quit action by default
		self.root.quit()

	def _window_minimize(self, event=None):
		""" _window_minimize """
		print('DEBUG: Window Minimize clicked', event)
		self._root.iconify()

	def _window_fullscreen(self, event=None):
		""" _window_fullscreen """
		print('DEBUG: Window Fullscreen clicked', event)
		self._fullscreen = not self._fullscreen
		self._root.attributes(fullscreen=self._fullscreen)

	def _menu_export(self, event=None):
		""" _menu_export """
		print('DEBUG: Export clicked', event)

	def _menu_quit(self, event=None):
		""" _menu_quit """
		print('DEBUG: Quit clicked', event)
		self.root.quit()

	def _show_preferences(self):
		""" _show_preferences """
		print('DEBUG: Show Preferences clicked')

	def _show(self, show):
		""" _show """
		if show:
			print('DEBUG: Show event')
		else:
			# could stop timers etc etc
			print('DEBUG: Hide event')

	def _handle_escape(self, event=None):
		""" _handle_escape """
		print('DEBUG: Escape clicked', event)
		# for now we just stop the acceleration - but will do more later.
		self.accelerate_button_off()

	def _set_menubar_and_keyboard(self):
		""" _set_menubar_and_keyboard """

		self._fullscreen = False

		self._menubar = tk.Menu(self.root)

		self.root.option_add('*tearOff', False)

		if self._window_system == 'aqua':
			# MacOS
			command = 'Command'
		else:
			# Windows and Linux
			command = 'Control'

		# File menu ...
		file_menu = tk.Menu(self._menubar, tearoff=False)
		file_menu.add_command(label='New...', accelerator=command+'+N', command=self._menu_new_file)
		file_menu.add_command(label='Open', accelerator=command+'+O', command=self._menu_open_file)
		file_menu.add_command(label='Save...', accelerator=command+'+S', command=self._menu_save_file)
		file_menu.add_command(label='Export', command=self._menu_export)
		file_menu.add_command(label='Close Window', accelerator=command+'+W', command=self._window_close)
		file_menu.add_separator()
		# Quit does not belong on the File menu bar on MacOS ... but does on other OS's
		if self._window_system != 'aqua':
			file_menu.add_command(label='Quit', accelerator=command+'+Q', command=self._menu_quit)
		self._menubar.add_cascade(label='File', menu=file_menu)

		# Help menu ...
		help_menu = tk.Menu(self._menubar, tearoff=False)
		help_menu.add_command(label='Help', accelerator=command+'+H', command=self._show_help_info)
		help_menu.add_separator()
		help_menu.add_command(label='About', command=self._show_about_info)
		self._menubar.add_cascade(label='Help', menu=help_menu)

		# Window menu ...
		window_menu = tk.Menu(self._menubar, tearoff=False)
		window_menu.add_command(label='Minimize', accelerator=command+'+M', command=self._window_minimize)
		window_menu.add_command(label='Fill', accelerator='Control+'+command+'+F', command=self._window_fullscreen)
		self._menubar.add_cascade(label='Window', menu=window_menu)

		# add the menubar
		self.root.config(menu=self._menubar)

		# special case code for specific os's ... sadly
		if self._window_system == 'aqua':
			# special case on Mac ... add to apple menu ... https://www.tcl-lang.org/man/tcl/TkCmd/tk_mac.html
			self.root.createcommand('tk::mac::Quit', self._menu_quit)
			# why isn't this ... 'tk::mac::ShowAboutBox'
			self.root.createcommand('tkAboutDialog', self._show_about_info)
			self.root.createcommand('tk::mac::ShowPreferences', self._show_preferences)

			self.root.createcommand('tk::mac::OnHide', lambda: self._show(False))
			self.root.createcommand('tk::mac::OnShow', lambda: self._show(True))

		self.root.bind_all('<'+command+'-h>', self._show_help_info)
		self.root.bind_all('<'+command+'-H>', self._show_help_info)
		self.root.bind_all('<'+command+'-n>', self._menu_new_file)
		self.root.bind_all('<'+command+'-N>', self._menu_new_file)
		self.root.bind_all('<'+command+'-o>', self._menu_open_file)
		self.root.bind_all('<'+command+'-O>', self._menu_open_file)
		self.root.bind_all('<'+command+'-s>', self._menu_save_file)
		self.root.bind_all('<'+command+'-S>', self._menu_save_file)
		self.root.bind_all('<'+command+'-w>', self._window_close)
		self.root.bind_all('<'+command+'-W>', self._window_close)

		self.root.bind_all('<'+command+'-m>', self._window_minimize)
		self.root.bind_all('<'+command+'-M>', self._window_minimize)
		self.root.bind_all('<Control-'+command+'-f>', self._window_fullscreen)
		self.root.bind_all('<Control-'+command+'-F>', self._window_fullscreen)

		# These are added on all OS's as MacOS uses this via main menu item
		self.root.bind_all('<'+command+'-q>', self._menu_quit)
		self.root.bind_all('<'+command+'-Q>', self._menu_quit)

		# We do this becuase we sometimes want to stop things
		self.root.bind_all('<Escape>', self._handle_escape)

	# CAMERA MENU

	def create_camera_menu(self, list_of_cameras):
		""" create__camera_select """
		# Camera selection menu ...
		camera_menu = tk.Menu(self._menubar, tearoff=False)
		for camera_name in list_of_cameras:
			camera_menu.add_command(label=camera_name, command=lambda camera_name=camera_name: self._camera_select(camera_name))
		self._menubar.insert_cascade(1, label='Camera', menu=camera_menu)

	def _camera_select(self, camera_name:str):
		""" _camera_select """
		self.core.do_camera_select(camera_name)

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

	def accelerate_button_off(self):
		""" accelerate_button_off """
		if self._accelerate_state.get():
			# accelerate is on
			self._accelerate_button.invoke()

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

	def star_mag_buttons(self, parent, row, col, star_magnitudes):
		""" star_mag_buttons """
		lf = self.labelframe(parent, 'Star Magnitude')
		lf.grid(row=row, column=col)
		m_default = 5.0
		self._star_mag_buttons_variable = tk.DoubleVar(value=m_default)
		for m,v in star_magnitudes.items():
			# radiobutton
			b = ttk.Radiobutton(lf, text='%.1f (%d stars)' % (m,v), variable=self._star_mag_buttons_variable, value=m, command=lambda value=m: self.do_mag(value))
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

	# Bring to front after a small delay to allow for app init
	def _center_and_delayed_bring_to_front_and_make_focus(self):
		""" _center_and_delayed_bring_to_front_and_make_focus """
		# center app window on screen
		self.root.update_idletasks()
		app_width = self.root.winfo_reqwidth()
		app_height = self.root.winfo_reqheight()
		x = (self.root.winfo_screenwidth() / 2) - (app_width / 2)
		y = (self.root.winfo_screenheight() / 2) - (app_height / 2)
		self.root.geometry('%dx%d+%d+%d' % (app_width, app_height, x, y))
		# now make sure app is fully in focus
		self.root.deiconify()			# Bring back if minimized
		self.root.lift()			# Bring to top of Z-order
		self.root.attributes('-topmost', True)	# Set always on top
		self.root.focus_force()
		self.root.attributes('-topmost', False)	# Optional: set to False to allow other apps over it


	def mainloop(self):
		""" mainloop """
		_ = self.root.after(1, lambda: self._center_and_delayed_bring_to_front_and_make_focus())
		self.root.mainloop()
