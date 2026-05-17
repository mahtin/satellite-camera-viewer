""" CameraImage """

from PIL import Image, ImageDraw, ImageTk

class CameraImage:
	""" CameraImage """

	def __init__(self, width=400, height=300):
		""" CameraImage """
		self._width = width
		self._height = height
		self._pil_img = Image.new('RGB', (self._width, self._height), color=(127, 127, 127))
		self._draw = ImageDraw.Draw(self._pil_img, "RGB")

	@property
	def image(self):
		""" image """
		self._photo_img = ImageTk.PhotoImage(self._pil_img)
		return self._photo_img

	def paint(self, where):
		""" paint """
		where.configure(image=self.image)

	def save(self):
		""" save """
		self._pil_img.save('/tmp/camera.png', "PNG")

	def line(self, xy1, xy2, color=(0,0,0), width=1):
		""" line """
		self._draw.line((xy1, xy2), fill=color, width=width)

	def circle(self, xy, radius=1, color=(0,0,0), width=1):
		""" circle """
		self._draw.circle(xy, radius, fill=color, width=width)

	def clear(self, color=(255,255,255)):
		""" clear """
		xy = [
			(0            ,              0),
			(self._width-1, self._height-1)
		]
		self._draw.rectangle(xy, fill=color, outline=color, width=1)

def _main(args=None):
	""" _main """

	from PIL import __version__
	print('PIL version =', __version__)

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
