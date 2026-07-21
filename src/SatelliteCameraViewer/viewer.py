""" viewer """

import warnings

from .core import CoreCode
from .ui import UserInterface
from .static_list_satellites import static_list_satellites

# Turn all RuntimeWarnings into exceptions
warnings.filterwarnings('error', category=RuntimeWarning)

def viewer(args=None):
	"""
	viewer - main code to start all of SatelliteCameraViewer app.

	:param args: Any CLI args
	:type args: list[str] | None

	This code only exits when the main window (or app) is closed and/or via ^C.

	"""

	# start UI first
	ui = UserInterface(title='Satellite Camera Viewer')
	# start core and pass it the UI
	_ = CoreCode(ui=ui)
	# now core knows ui and ui knows core ... we continue just referencing ui from this point onwards
	# ui = core.ui & core = ui.core ... QED

	list_of_cameras = ui.core.my_camera.camera.CameraSensors.keys()
	ui.create_camera_menu(list_of_cameras)

	# all the frames ...
	top_frame = ui.frame(ui.root, padx=0, pady=0, borderwidth=0, anchor='n')
	bottom_frame = ui.frame(ui.root, padx=0, pady=0, borderwidth=0, anchor='n')
	# top
	starfield_graph_frame = ui.frame(top_frame, col=0, padx=1, pady=1, borderwidth=0, sticky='nw')
	adjustments_frame = ui.frame(top_frame, col=1, padx=1, pady=1, borderwidth=0, sticky='ne')
	# bottom
	info_frame = ui.labelframe(bottom_frame, 'Info', col=0, padx=1, pady=1, borderwidth=0)
	photo_frame = ui.labelframe(bottom_frame, 'Camera',  col=1, padx=1, pady=1, borderwidth=1)
	earth_frame = ui.labelframe(bottom_frame, 'Earth', col=2, padx=1, pady=1, borderwidth=1)
	sat_frame = ui.labelframe(bottom_frame, 'Satellite', col=3, padx=1, pady=1, borderwidth=1)

	# start the graphing for the starfield!
	ui.core.plot_in_tk(starfield_graph_frame, 'starfield')

	row = 0
	col = 0

	# various buttons
	buttons_frame = ui.frame(adjustments_frame, row=row, col=col, padx=0, pady=0,  borderwidth=0, sticky='nw')
	row += 1

        # column 0
	b_row = 0
	b_col = 0
	ui.accelerate_button(buttons_frame, b_row, b_col)
	b_row += 1
	ui.stars_button(buttons_frame, b_row, b_col)
	b_row += 1
	ui.match_stars_button(buttons_frame, b_row, b_col)
	b_row += 1

        # column 1
	b_col += 1
	b_row = 0
	ui.planets_etc_button(buttons_frame, b_row, b_col)
	b_row += 1
	ui.constellation_boundaries_button(buttons_frame, b_row, b_col)
	b_row += 1
	ui.earth_vector_button(buttons_frame, b_row, b_col)
	b_row += 1

	# TODO add more buttons here.

	# focal length and star magnitude choices

	choices_frame = ui.frame(adjustments_frame, row=row, col=col, padx=0, pady=0,  borderwidth=0, sticky='nw')
	row += 1

	def setup_star_magnitude(parent):
		""" setup_star_magnitude """
		mag_frame = ui.frame(parent, padx=0, borderwidth=0, sticky='nw')
		# The BSC5 catalog is best used with the following steps:
		#   MAG  COUNT      %
		#   1.0     15   0.2%
		#   5.0   1630  17.9%
		#   6.0   5080  55.8%
		#   8.0   9096 100.0%
		star_magnitudes = {1.0: 15, 5.0: 1630, 6.0: 5080, 8.0: 9096}
		m_row = 0
		m_col = 0
		ui.star_mag_buttons(mag_frame, m_row, m_col, star_magnitudes)
		m_row += len(star_magnitudes)

	def setup_focal_length(parent):
		""" setup_focal_length """
		focal_length_frame = ui.frame(parent, col=1, padx=0, borderwidth=0, sticky='ne')
		focal_lengths = [35, 50, 100, 200, 400]
		f_row = 0
		f_col = 0
		ui.focal_length_buttons(focal_length_frame, f_row, f_col, focal_lengths)
		f_row += len(focal_lengths)

	# satellite selection
	def setup_satellite_selection(parent):
		""" setup_satellite_selection """
		satellite_frame = ui.labelframe(parent, 'Satellite Selection', row=row, col=0, colspan=2, sticky='nw')
		s_row = 0
		s_col = 0

		# 1) satellite selection section
		satellite_names = [v.name for v in static_list_satellites]
		ui.satellite_selection(satellite_frame, s_row, s_col, satellite_names)
		s_row += 1

		# 2) satellite camera pointing section
		attitude_names = ['vv', 'nadir', 'ground', 'star']
		ui.satellite_attitude_buttons(satellite_frame, s_row, s_col, attitude_names)
		s_row += 1

	setup_focal_length(choices_frame)
	setup_star_magnitude(choices_frame)
	row += 1
	setup_satellite_selection(choices_frame)
	row += 1

	# # slider info text - presently not displayed
	# ui.rpy_label(adjustments_frame, row, col)
	# row += 1

	# three sliders for camera yaw/pitch/roll
	ui.rpy_sliders(adjustments_frame, row, col)
	row += 1

	# reset button
	ui.reset_everything_button(adjustments_frame, row, col)
	row += 1

	nx = ui.core.my_camera.camera.nx
	ny = ui.core.my_camera.camera.ny
	h = 200
	w = int(h * nx/ny)

	# place photo image here ...
	col = 0
	row = 0
	photo_label = ui.photo_label(photo_frame, row, col, width=w, height=h)
	photo_label.grid(row=0, column=0, padx=2, pady=2, sticky='ne')
	ui.core.camera_image_register(label=photo_label, nx=nx, ny=ny, w=w, h=h)

	# place for an earth map ...
	ui.core.plot_in_tk(earth_frame, 'earth')

	# key values for cubesat display
	u = 1
	w = 225
	h = 200

	#  place satellite image here ...
	col = 0
	row = 0
	sat_label = ui.sat_label(sat_frame, row, col, width=w, height=h)
	sat_label.grid(row=0, column=0, padx=2, pady=2, sticky='ne')

	# build a 3D cubesat model
	# cubesat_model = Cubesat(u=u, width=w, height=h)
	# build the viewer for the cubesat 3D model
	# cubesat_viewer = CubesatViewer(image_canvas=sat_label, cubesat=cubesat_model, width=w, height=h)

	ui.core.cubesat_viewer_register(u=u, label=sat_label, w=w, h=h)

	col = 0
	row = 0
	# camera info box
	ui.camera_info_box(info_frame, row, col)

	row += 1
	# star found box
	ui.star_found_text_box(info_frame, row, col)

	row += 1
	# misc box
	ui.misc_text_box(info_frame, row, col)

	# prime everything the first time by runing timer expiry code once (which triggers it constant running)
	ui.core.timer_went_off()

	# the main loop - never to return (unless we exit)
	ui.mainloop()
	# not reached
