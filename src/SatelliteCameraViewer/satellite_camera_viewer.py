"""
satellite_camera_viewer - main CLI entry point
"""

import sys

from .viewer import viewer

def satellite_camera_viewer(args=None):
	"""
	satellite_camera_viewer - main CLI entry point

	Via pyproject.toml, this function is called from the CLI command.

	:param args: Command line arguments
	:type args: list[str] | None

	:return: None

	"""

	sys.exit(viewer(args))

def _main(args=None):
	""" _main """
	satellite_camera_viewer(args)

if __name__ == '__main__':
	_main()
