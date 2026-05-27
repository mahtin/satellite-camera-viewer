""" ui.py """

import tkinter as tk
from tkinter import ttk

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

		# configure UI gloablly first
		self._root.option_add('*Font', (self.font['family'], self.font['size'] - 2))

		self._style = ttk.Style()
		self._style.configure('Horizontal.TScale', sliderthickness=0, borderwidth=0, sliderlength=0)	# does not work - hence zeros
		self._style.configure('TCheckbutton', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TMenubutton', font=(self.font['family'], self.font['size']-2, ''))
		self._style.configure('TRadiobutton', justify='left',  font=(self.font['family'], self.font['size']-2, ''))

		self._core = None
		self._title_label = None
		self._camera_info_box = None
		self._star_found_text_box = None
		self._misc_text_box = None
		self._realtime_button = None
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

	def frame(self, parent, borderwidth=1, relief='solid', row=0, col=0, padx=5, pady=2, sticky='nsew', anchor=None):
		""" frame """
		f = ttk.Frame(parent, borderwidth=borderwidth, relief=relief)
		if anchor is not None:
			f.pack(padx=padx, pady=pady, anchor=anchor)
		else:
			f.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
		return f

	def labelframe(self, parent, text='', borderwidth=1, relief='solid', row=0, col=0, padx=5, pady=2, sticky='nsew'):
		""" labelframe """
		f = ttk.LabelFrame(parent, text=text, borderwidth=borderwidth, relief=relief)
		f.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
		return f

	# TITLE

	#def title_label(self, parent, text):
	#	""" title_label """
	#	l = ttk.Label(parent, text=text, justify='left', font=('', 24, 'bold'))
	#	l.pack(padx=5, pady=2)
	#	self._title_label = l

	# INFO TEXT BOXES

	def camera_info_box(self, parent, row, col):
		""" camera_info_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		self._camera_info_box = t

	def misc_text_box(self, parent, row, col):
		""" misc_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		self._misc_text_box = t

	def star_found_text_box(self, parent, row, col):
		""" star_found_text_box """
		t = tk.Text(parent, width=80, height=3, state='disabled', wrap=tk.WORD)
		t.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
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

	def do_realtime(self, value):
		""" do_realtime """
		self.core.do_realtime(value)

	def realtime_button(self, parent, row, col):
		""" realtime_button """
		self._realtime_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Accelerate?', variable=self._realtime_state, command=lambda value=self._realtime_state: self.do_realtime(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		self._realtime_button = b

	def realtime_button_set(self, value):
		""" realtime_button_set """
		self._realtime_state.set(value)

	def do_stars(self, value):
		""" do_stars """
		self.core.do_stars(value)

	def stars_button(self, parent, row, col):
		""" stars_button """
		self._stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Stars?', variable=self._stars_state, command=lambda value=self._stars_state: self.do_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		self._stars_button = b

	def stars_button_set(self, value):
		""" set_stars_button """
		self._stars_state.set(value)

	def do_match_stars(self, value):
		""" do_match_stars """
		self.core.do_match_stars(value)

	def match_stars_button(self, parent, row, col):
		""" match_stars_button """
		self._match_stars_state = tk.BooleanVar(value=False)
		b = ttk.Checkbutton(parent, text='Match stars?', variable=self._match_stars_state, command=lambda value=self._match_stars_state: self.do_match_stars(value))
		b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
		self._match_stars_button = b

	def match_stars_button_set(self, value):
		""" match_stars_button_set """
		self._match_stars_state.set(value)

	# STAR MAGNITUDE

	def do_mag(self, value):
		""" do_mag """
		self.core.do_mag(value)

	def star_mag_buttons(self, parent, row, col, mags):
		""" star_mag_buttons """
		#l = ttk.Label(parent, text='Star Magnitude', justify='left')
		#l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		#row += 1
		lf = self.labelframe(parent, 'Star Magnitude')
		lf.grid(row=row, column=col)
		m_default = mags[2]
		self._star_mag_buttons_variable = tk.DoubleVar(value=m_default)
		for m in mags:
			# radiobutton
			b = ttk.Radiobutton(lf, text='%.1f' % m, variable=self._star_mag_buttons_variable, value=m, command=lambda value=m: self.do_mag(value))
			b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
			self._star_mag_buttons[m] = b
			row += 1

	def star_mag_buttons_set(self, mag=5.0):
		""" star_mag_buttons_set """
		self._star_mag_buttons_variable.set(mag)

	# FOCAL LENGTH

	def do_focal_length(self, f):
		""" do_focal_length """
		self.core.do_focal_length(f)

	def focal_length_buttons(self, parent, row, col, focal_lengths):
		""" focal_length_buttons """
		# l = ttk.Label(parent, text='Focal Length', justify='left')
		# l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		# row += 1
		lf = self.labelframe(parent, 'Focal Length')
		lf.grid(row=row, column=col)
		f_default = focal_lengths[1]
		self._focal_length_buttons_variable = tk.IntVar(value=f_default)
		for f in focal_lengths:
			# radiobutton
			b = ttk.Radiobutton(lf, text='%d mm' % f, variable=self._focal_length_buttons_variable, value=f, command=lambda f=f: self.do_focal_length(f))
			b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
			self._focal_length_buttons[f] = b
			row += 1

	def focal_length_buttons_set(self, focal_length=50):
		""" focal_length_set """
		self._focal_length_buttons_variable.set(focal_length)

	# SATELLITE SELECTION

	def do_satellite_selection(self, val):
		""" do_satellite_selection """
		self.core.do_satellite_selection(val)

	def satellite_selection(self, parent, row, col, satellite_names):
		""" satellite_selection """
		# l = ttk.Label(parent, text='Satellite Selection', justify='left')
		# l.grid(row=row, column=col, columnspan=7, padx=5, pady=2, sticky='nsew')
		# row += 1
		lf = self.labelframe(parent, 'Satellite Selection')
		lf.grid(row=row, column=col, columnspan=7, sticky='ew')
		s_default = satellite_names[0]
		self._satellite_selected = tk.StringVar(value=s_default)
		drop = ttk.OptionMenu(lf, self._satellite_selected, *satellite_names, command=lambda val: self.do_satellite_selection(val))
		drop.grid(row=row, column=col, columnspan=7, padx=5, pady=2, sticky='ew')
		self._satellite_selection_drop = drop

	# SATELLITE BUTTONS

	def do_satellite_attitude(self, a):
		""" do_satellite_attitude """
		self.core.do_satellite_attitude(a)

	def satellite_attitude_buttons(self, parent, row, col, attitude_names):
		""" satellite_attitude_buttons """
		a_default = attitude_names[0]
		self._satellite_attitude_buttons_variable = tk.IntVar(value=a_default)
		for a in attitude_names:
			# radiobutton
			b = ttk.Radiobutton(parent, text=a, variable=self._satellite_attitude_buttons_variable, value=a, command=lambda a=a: self.do_satellite_attitude(a))
			b.grid(row=row, column=col, padx=5, pady=2, sticky='nw')
			self._satellite_attitude_buttons[a] = b
			col += 1

	# ROLL PITCH YAW

	def rpy_label(self, parent, text, row, col):
		""" rpy_label """
		rpy_label = 'Roll(X) / Pitch(Y) / Yaw(Z) controls for satellite body (and hence camera)'
		l = ttk.Label(parent, text=rpy_label, justify='left', wraplength=160)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		self._rpy_label = l

	def do_rpy(self, val, k):
		""" do_rpy """
		self.core.do_rpy(val, k)

	def rpy_sliders(self, parent, row, col):
		""" rpy_sliders """
		lf = self.labelframe(parent, 'Attitude')
		lf.grid(row=row, column=col, sticky='ew')
		self.v_sliders = {}
		for k,v in self.rpy_values_deg.items():
			l = ttk.Label(lf, text=self._cam_slider_rpy_text[k], justify='left')
			l.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
			row += 1
			self.v_sliders[k] = tk.IntVar(value=int(v))
			s = ttk.Scale(lf,
				# label=self._cam_slider_rpy_text[k],
				variable=self.v_sliders[k],
				from_=-90, to=90,
				# resolution=10.0,
				# showvalue=True,
				orient='horizontal',
				command=lambda val,k=k: self.do_rpy(val, k))
			s.grid(row=row, column=col, padx=5, pady=2, sticky='w')
			self._rpy_sliders[k] = s
			row += 1

	# 3D cubesat image

	def sat_label(self, parent, row, col, width=300, height=300):
		""" sat_label """
		l = tk.Label(parent, bg='whitesmoke', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
		self._sat_label = l
		return self._sat_label

	# photo image

	def photo_label(self, parent, row, col, width=300, height=300):
		""" photo_label """
		l = tk.Label(parent, bg='cyan', borderwidth=0, width=width, height=height)
		l.grid(row=row, column=col, padx=5, pady=2, sticky='w')
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
		b = ttk.Button(parent, text='RESET EVERYTHING', style='Reset.TButton', command=lambda: self.do_reset())
		b.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
		self._reset_everything_button = b

	def mainloop(self):
		""" mainloop """
		self.root.mainloop()
