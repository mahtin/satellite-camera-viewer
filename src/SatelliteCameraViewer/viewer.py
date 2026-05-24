""" viewer """

import sys
import warnings
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .core import CoreCode
from .ui import UserInterface
from .static_tles import static_tles

# Turn all RuntimeWarnings into exceptions
warnings.filterwarnings('error', category=RuntimeWarning)

def viewer(args=None):
	"""
	viewer - main code to start all of SatelliteCameraViewer app.

	:param args: Any CLI args
	:type args: list[str] | None

	This code only exits when the window is close and/or via ^C.

	"""
	root = tk.Tk()

	# --- Matplotlib figure ---
	font = tk.font.nametofont("TkDefaultFont").actual()
	core_code = CoreCode(root=root, font_family=font['family'], font_size=font['size'])

	# {'family': '.AppleSystemUIFont', 'size': 13, 'weight': 'normal', 'slant': 'roman', 'underline': 0, 'overstrike': 0}

	root.title('Satellite Camera Viewer')

	UserInterface.register_core_code(core_code)

	UserInterface.title_label(root, 'Satellite Camera Viewer')

	top_frame = ttk.Frame(root, borderwidth=0, relief='solid')		# flat, groove, raised, ridge, solid, or sunken
	top_frame.pack(padx=5, pady=2, anchor='n')

	# a place for the starfield graph
	starfield_graph_frame = ttk.Frame(top_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	starfield_graph_frame.grid(row=0, column=0, padx=5, pady=2, sticky='n')

	adjustments_frame = ttk.Frame(top_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	adjustments_frame.grid(row=0, column=1, padx=5, pady=5, sticky='n')

	# now start the graphing starfield!
	canvas_for_starfield_graph = FigureCanvasTkAgg(core_code.starfield_fig, master=starfield_graph_frame)
	canvas_for_starfield_graph.get_tk_widget().grid(row=0, column=0, padx=5, pady=2, sticky='nsew')
	canvas_for_starfield_graph.draw()

	core_code.pyplot_starfield_canvas_area_register(canvas_for_starfield_graph)

	# various buttons
	row = 0
	col = 0
	UserInterface.realtime_button(adjustments_frame, row, col)
	row += 1

	UserInterface.stars_button(adjustments_frame, row, col)
	row += 1

	UserInterface.match_stars_button(adjustments_frame, row, col)
	row += 1

	# focal length and star magnitude choices

	choices_frame = ttk.Frame(adjustments_frame, borderwidth=0)	# flat, groove, raised, ridge, solid, or sunken
	choices_frame.grid(row=row, column=col, padx=0, pady=0, sticky='nw')
	row += 1

	def setup_star_magnitude(parent):

		# style = ttk.Style()
		# style.theme_use('classic')
		# style.configure('Star_mag.TFrame',
		# 	bordercolor='whitesmoke',
		# 	borderwidth=1,
		# )
		# ..., style='Star_mag.TFrame', ...

		mag_frame = ttk.Frame(parent, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
		mag_frame.grid(row=0, column=0, padx=2, pady=2, sticky='nw')
		star_magnitudes = [1.0, 3.0, 5.0, 7.0, 9.0]
		m_row = 0
		m_col = 0
		UserInterface.star_mag_buttons(mag_frame, m_row, m_col, star_magnitudes)
		m_row += len(star_magnitudes)

	def setup_focal_length(parent):
		focal_length_frame = ttk.Frame(parent, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
		focal_length_frame.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
		focal_lengths = [35, 50, 100, 200, 400]
		f_row = 0
		f_col = 0
		UserInterface.focal_length_buttons(focal_length_frame, f_row, f_col, focal_lengths)
		f_row += len(focal_lengths)

	setup_focal_length(choices_frame)
	setup_star_magnitude(choices_frame)

	# satellite selection
	def setup_satellite_selection(parent):
		""" setup_satellite_selection """
		satellite_frame = ttk.Frame(parent, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
		satellite_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
		satellite_names = [v.name for v in static_tles]
		s_row = 0
		s_col = 0
		UserInterface.satellite_selection(satellite_frame, s_row, s_col, satellite_names)
		s_row += 2
		attitude_names = ['vv', 'nadir', 'ground', 'star']
		UserInterface.satellite_attitude_buttons(satellite_frame, s_row, s_col, attitude_names)

	setup_satellite_selection(adjustments_frame)
	row += 1

	# # slider info text - presently not displayed
	# col = 0
	# UserInterface.rpy_label(adjustments_frame, row, col)
	# row += 1

	# three sliders for camera yaw/pitch/roll
	UserInterface.rpy_sliders(adjustments_frame, row, col)
	row += 3

	# reset button
	UserInterface.reset_everything_button(adjustments_frame, row, col)
	row += 1

	bottom_frame = ttk.Frame(root, borderwidth=0)	# flat, groove, raised, ridge, solid, or sunken
	bottom_frame.pack(padx=0, pady=0, anchor='n')

	row = 0
	col = 0
	info_frame = ttk.Frame(bottom_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	info_frame.grid(padx=5, pady=2, row=row, column=col, sticky='nsew')
	col += 1

	photo_frame = ttk.Frame(bottom_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	photo_frame.grid(padx=5, pady=2, row=row, column=col, sticky='nsew')
	col += 1

	earth_graph_frame = ttk.Frame(bottom_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	earth_graph_frame.grid(row=row, column=col, padx=5, pady=2, sticky='n')
	col += 1

	sat_frame = ttk.Frame(bottom_frame, borderwidth=1, relief='solid')	# flat, groove, raised, ridge, solid, or sunken
	sat_frame.grid(padx=5, pady=2, row=row, column=col, sticky='nsew')

	nx = core_code.nikon.camera.nx
	ny = core_code.nikon.camera.ny
	h = 200
	w = int(h * nx/ny)

	# place photo image here ...
	col = 0
	row = 0
	photo_label = UserInterface.photo_label(photo_frame, row, col, width=w, height=h)
	photo_label.grid(row=0, column=0, padx=5, pady=2, sticky='ne')

	core_code.camera_image_register(label=photo_label, nx=nx, ny=ny, w=w, h=h)

	# place for an earth map ...
	col = 0
	row = 0
	canvas_for_earth_graph = FigureCanvasTkAgg(core_code.earth_fig, master=earth_graph_frame)
	canvas_for_earth_graph.get_tk_widget().grid(row=row, column=row, padx=5, pady=2, sticky='nsew')
	canvas_for_earth_graph.draw()

	core_code.pyplot_earth_canvas_area_register(canvas_for_earth_graph)

	# key values for cubesat display
	u = 1
	w = 225
	h = 200

	#  place satellite image here ...
	col = 0
	row = 0
	sat_label = UserInterface.sat_label(sat_frame, row, col, width=w, height=h)
	sat_label.grid(row=0, column=0, padx=5, pady=2, sticky='ne')

	# build a 3D cubesat model
	# cubesat_model = Cubesat(u=u, width=w, height=h)
	# build the viewer for the cubesat 3D model
	# cubesat_viewer = CubesatViewer(image_canvas=sat_label, cubesat=cubesat_model, width=w, height=h)

	core_code.cubesat_viewer_register(u=u, label=sat_label, w=w, h=h)

	col = 0
	row = 0
	# camera info box
	UserInterface.camera_info_box(info_frame, row, col)

	row += 1
	# star found box
	UserInterface.star_found_text_box(info_frame, row, col)

	row += 1
	# misc box
	UserInterface.misc_text_box(info_frame, row, col)

	# prime everything by runing timer expiry code
	core_code.timer_went_off()

	# Bring to front after a small delay to allow for app init
	def center_and_delayed_bring_to_front_and_make_focus(root):
		""" center_and_delayed_bring_to_front_and_make_focus """
		# center app window on screen
		root.update_idletasks()
		app_width = root.winfo_reqwidth()
		app_height = root.winfo_reqheight()
		x = (root.winfo_screenwidth() / 2) - (app_width / 2)
		y = (root.winfo_screenheight() / 2) - (app_height / 2)
		root.geometry('%dx%d+%d+%d' % (app_width, app_height, x, y))
		# now make sure app is fully in focus
		root.deiconify()			# Bring back if minimized
		root.lift()				# Bring to top of Z-order
		root.attributes('-topmost', True)	# Set always on top
		root.focus_force()
		root.attributes('-topmost', False)	# Optional: set to False to allow other apps over it

	_ = root.after(1, lambda: center_and_delayed_bring_to_front_and_make_focus(root))

	root.mainloop()

def _main(args=None):
	""" _main """
	try:
		viewer(args)
	except KeyboardInterrupt as e:
		sys.exit(e)
	sys.exit(0)

if __name__ == '__main__':
	_main()
