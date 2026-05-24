""" ui.py """

import tkinter as tk
from tkinter import ttk

class UserInterface:
	""" UserInterface """

	_core_code = None
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
		'roll': 0.0,		# X
		'pitch': 0.0,		# Y
		'yaw': 0.0		# Z
	}
	""" rpy_values_deg - values of Roll, Pitch, and Yaw sliders. """

	_cam_slider_rpy_text = {
		'roll': 'Roll (X) side-to-side',
		'pitch': 'Pitch (Y) nose-up-down',
		'yaw': 'Yaw((Z) left-right'
	}

	@classmethod
	def register_core_code(cls, f):
		""" register_core_code """
		cls._core_code = f

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
		cls._core_code.do_realtime(value)

	@classmethod
	def realtime_button(cls, parent, row, col):
		""" realtime_button """
		cls._realtime_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Accelerate?', variable=cls._realtime_state, command=lambda value=cls._realtime_state: cls.do_realtime(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		cls._realtime_button = b

	@classmethod
	def realtime_button_set(cls, value):
		""" realtime_button_set """
		cls._realtime_state.set(value)

	@classmethod
	def do_stars(cls, value):
		""" do_stars """
		cls._core_code.do_stars(value)

	@classmethod
	def stars_button(cls, parent, row, col):
		""" stars_button """
		cls._stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Stars?', variable=cls._stars_state, command=lambda value=cls._stars_state: cls.do_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		cls._stars_button = b

	@classmethod
	def stars_button_set(cls, value):
		""" set_stars_button """
		cls._stars_state.set(value)

	@classmethod
	def do_match_stars(cls, value):
		""" do_match_stars """
		cls._core_code.do_match_stars(value)

	@classmethod
	def match_stars_button(cls, parent, row, col):
		""" match_stars_button """
		cls._match_stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Match stars?', variable=cls._match_stars_state, command=lambda value=cls._match_stars_state: cls.do_match_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		cls._match_stars_button = b

	@classmethod
	def match_stars_button_set(cls, value):
		""" match_stars_button_set """
		cls._match_stars_state.set(value)

	# STAR MAGNITUDE

	@classmethod
	def do_mag(cls, value):
		""" do_mag """
		cls._core_code.do_mag(value)

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
		cls._core_code.do_focal_length(f)

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

	# SATELLITE SELECTION

	@classmethod
	def do_satellite_selection(cls, val, satellites):
		""" do_satellite_selection """
		cls._core_code.do_satellite_selection(val)

	@classmethod
	def satellite_selection(cls, parent, row, col, satellites):
		""" satellite_selection """
		l = ttk.Label(parent, text='Satellite Selection', justify='left')
		l.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		row += 1
		s_default = satellites[0]
		cls._satellite_selected = tk.StringVar(value=s_default)
		drop = tk.OptionMenu(parent, cls._satellite_selected, *satellites, command=lambda val, satellites=satellites: cls.do_satellite_selection(val, satellites))
		drop.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		cls._satellite_selection_drop = drop

	# ROLL PITCH YAW

	@classmethod
	def rpy_label(cls, parent, text, row, col):
		""" rpy_label """
		rpy_label = 'Roll(X) / Pitch(Y) / Yaw(Z) controls for satellite body (and hence camera)'
		l = ttk.Label(parent, text=rpy_label, justify='left', wraplength=160)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		cls._rpy_label = l

	@classmethod
	def do_rpy(cls, val, k):
		""" do_rpy """
		cls._core_code.do_rpy(val, k)

	@classmethod
	def rpy_sliders(cls, parent, row, col):
		""" rpy_sliders """
		cls.v_sliders = {}
		for k,v in cls.rpy_values_deg.items():
			cls.v_sliders[k] = tk.IntVar(value=int(v))
			s = tk.Scale(parent, label=cls._cam_slider_rpy_text[k], variable=cls.v_sliders[k], from_=-90, to=90, resolution=10.0, showvalue=True,
				orient='horizontal', command=lambda val,k=k: cls.do_rpy(val, k))
			s.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
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
		cls._core_code.do_reset()

	@classmethod
	def reset_everything_button(cls, parent, row, col):
		""" reset_everything_button """
		font = tk.font.nametofont('TkDefaultFont').actual()
		style = ttk.Style()
		style.configure('Reset.TButton',
			foreground='lightcoral',
			font=(font['family'], font['size'], 'bold'),
		)
		b = ttk.Button(parent, text='RESET EVERYTHING', style='Reset.TButton', command=lambda: cls.do_reset())
		b.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		cls._reset_everything_button = b
