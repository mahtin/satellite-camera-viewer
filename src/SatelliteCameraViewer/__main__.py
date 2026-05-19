"""
satellite_camera_viewer - main CLI entry point
"""

import sys

from .viewer import viewer

def main(args=None):
	"""
	main - main CLI entry point

	:param args: Command line arguments
	:type args: list(str)

	"""

	sys.exit(viewer(args))

if __name__ == '__main__':
	main()
