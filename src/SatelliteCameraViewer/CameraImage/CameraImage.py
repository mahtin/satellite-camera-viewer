""" CameraImage """

from PIL import Image, ImageDraw, ImageTk

class CameraImage:
	"""
	CameraImage - manages the image drawing for the camera image

	:param width: Image width
	:type width: int
	:param height: Image height
	:type height: int

	"""

	def __init__(self, width=400, height=300):
		""" __init __ """
		self._width = width
		self._height = height
		self._pil_img = Image.new('RGB', (self._width, self._height), color=(127, 127, 127))
		self._draw = ImageDraw.Draw(self._pil_img, "RGB")

	def paint(self, where):
		"""
		paint - paints the image into the tkinter label

		:param where: The tkinter label.
		:type where: tkinter.Label

		"""
		where.configure(image=self.image)

	def save(self):
		"""
		save - write image to a temporary file in /tmp/ folder.
		"""
		self._pil_img.save('/tmp/camera.png', "PNG")

	def line(self, xy1, xy2, color=(0,0,0), width=1):
		"""
		line - draw a line.

		:param xy1: Start of line as an (x,y) tuple.
		:type xy1: tuple[float, float]
		:param xy2: Start of line as an (x,y) tuple.
		:type xy2: tuple[float, float]
		:param color: Color of line as an (r,g,b) tuple.
		:type color: tuple[int, int, int]
		:param width: Line width.
		:type width: float

		"""
		self._draw.line((xy1, xy2), fill=color, width=width)

	def circle(self, xy, radius, color=(0,0,0), width=1):
		"""
		circle - draw a circle.

		:param xy1: Center of circle as an (x,y) tuple.
		:type xy1: tuple[float, float]
		:param radius: Circle radius.
		:type radius: float
		:param color: Color of circle as an (r,g,b) tuple.
		:type color: tuple[int, int, int]
		:param width: circle outline width.
		:type width: float

		"""
		self._draw.circle(xy, radius, fill=color, width=width)

	def clear(self, color=(255,255,255)):
		"""
		clear - clear image.
		"""
		xy = [
			(0            ,              0),
			(self._width-1, self._height-1)
		]
		self._draw.rectangle(xy, fill=color, outline=color, width=1)

	@property
	def image(self):
		"""
		image - returns a tkinter-compatible photo image.

		:return: image
		:type: PIL.ImageTk.PhotoImage

		"""
		self._photo_img = ImageTk.PhotoImage(self._pil_img)
		return self._photo_img

def _main(args=None):
	""" _main """

	w = 400
	h = 400
	ci = CameraImage(w, h)

	ci.clear()
	ci.circle((  20,   20),  5)
	ci.circle((w-20,   20), 10)
	ci.circle((  20, h-20), 15)
	ci.circle((w-20, h-20), 20)

	ci.save()

if __name__ == '__main__':
	_main()
