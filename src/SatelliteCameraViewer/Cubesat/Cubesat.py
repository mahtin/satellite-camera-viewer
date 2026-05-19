"""
Cubesat with rotations using pyvista and shown in a tk window (using Label)
"""

import math
from dataclasses import dataclass

import numpy as np
import pyvista as pv
from PIL import Image, ImageTk, ImageDraw

@dataclass
class WDH:
    """
    WDH - Width, Depth, Height - used to store sizes of satellite cube.

    :param w: Width.
    :type w: float
    :param d: Height.
    :type d: float
    :param h: Depth.
    :type h: float

    Used intenally to Cubesat class, not really useful outside of core Cubesat code.
    """
    w: float = 0.0
    """ w - Width. """
    d: float = 0.0
    """ d - Depth. """
    h: float = 0.0
    """ h - Height. """

    @property
    def array(self):
        """
        array - return [w, d, h] as an array.

        :return: [w, d, h] as an array
        :type: list[float] | np.array
        """
        return np.array([[self.w, self.d, self.h]], dtype=float)

    def __array__(self, dtype=None):
        """ Allows np.array(instance) to work """
        return np.array([[self.w, self.d, self.h]], dtype=dtype)

    def __mul__(self, other):
        """ __mul__ """
        return WDH(self.w * other, self.d * other, self.h * other)

    def __str__(self):
        """ __str__ """
        return 'WDH[%f,%f,%f]' % (self.w, self.d, self.h)

class Cubesat:
    """
    Cubesat - Draw a cubesat in 3d via pyvista. This expects to be called with a tk window (using Label) as the location to paint the 3d image.
    """

    CM = 0.01
    """ CM - Centimeter (with Meter == 1). """
    MM = 0.001
    """ MM - Milimeter (with Meter == 1). """
    U = 10 * 0.01      # Cubesat basic measurement is a 'U' or 10cm
    """ U - Size of a single U (in Meters) from the Cubesat definition. """

    # CubeSat Design Specification (Rev. 14.1) from Cal Poly – San Luis Obispo, CA
    # 1U 1.5U 2U 3U 6U 12U
    _CubesatSpecSizes = {
        1:    WDH(1, 1, 1  ),
        1.5:  WDH(1, 1, 1.5),
        2:    WDH(1, 1, 2  ),
        3:    WDH(1, 1, 3  ),
        6:    WDH(2, 1, 3  ),
        8:    WDH(1, 2, 4  ),        # https://space-inventor.com/satellites/8u-satellite
        12:   WDH(2, 2, 3  ),
        16:   WDH(2, 2, 4  ),        # https://spire.com/spirepedia/nanosatellite-16u/
        27:   WDH(3, 3, 3  ),        # https://www.eoportal.org/other-space-activities/cubesat-deployer-standards
    }

    def __init__(self, u=3, width=800, height=800, isometric_view=False, show_axes=False):
        """
        Cubesat - Draw a cubesat in 3d via pyvista.

        :param u: Cubesat U size.
        :type u: int
        :param width: Width of graphics area.
        :type width: int
        :param height: Height of graphics area.
        :type height: int
        :param isometric_view: If True, visually representing three-dimensional objects in two dimensions.
        :type isometric_view: bool
        :param show_axes: If True, show the pyvista XYZ axis graphic.
        :type show_axes: bool
        """

        try:
            self._u = self._CubesatSpecSizes[u]
        except KeyError:
            raise ValueError('%s: invalid U value' % (u)) from None
        self._width = width
        self._height = height
        self._isometric_view = isometric_view
        self._build(show_axes)

    def _build(self, show_axes):
        """ _build """
        # PyVista off-screen plotter
        self._plotter = pv.Plotter(off_screen=True, window_size=(self._width, self._height))

        # caculate CubeSat geometry
        self._geometry_calculate()
        # add all the actors/parts
        self._add_parts()
        # add meshes for all parts/actors
        self._add_meshes()

        if show_axes:
            # We can drop these axes's later when all x,y,z are confirmed and debug done
            self._plotter.add_axes()

        if self._isometric_view:
            self._plotter.view_isometric(render=False)
        else:
            # reset_camera() automatically calculates a camera position, focal point,
            # and view-up vector that frames all actors in the scene. No need for any
            # call to Plotter.set_position([...])
            self._plotter.reset_camera(render=False)     # we will render later

    def render(self):
        """
        render - Do the render of the 3d object.

        :return: The image of the 3d object as a screenshot from the current camera position.
        :type: pyvista.pyvista_ndarray
        """
        # PyVista off-screen plotter can be rendered to an image
        self._plotter.render()
        return self._plotter.screenshot(return_img=True, transparent_background=True)

    # ============================================================
    # CubeSat geometry builder
    # ============================================================

    def _geometry_calculate(self):
        """ _geometry_calculate """
        self._body = self._u * self.U
        self._wall = 3 * self.MM

        # camera body outside of cubesat (XXX TODO maybe this is wrong - real cameras are inside)
        self._camera_offset = 4.0 * self.CM        # 4 cm from edge
        self._camera_radius = 40.0 * self.MM       # 40mm camera size
        self._camera_length = 40.0 * self.MM       # 40mm camera size
        self._camera_center = (0.0, self._body.d/2 + 0*self._camera_radius/2, -self._body.h/2 + self._camera_offset)

        # 16mm 10MP Telephoto lens dimensions 39mm diamater by 50mm length (XXX TODO should not stick out)
        self._lens_radius = 39.0/2 * self.MM       # 39mm lens lens
        self._lens_length = 50.0 * self.MM         # 50mm camera size

        # 70cm band
        self._antenna_length = 17.3 * self.CM    # 17.3 cm is 1/4 wave at 70cm (435–438 Mhz)

        # roll/pitch/yaw rotation point - hint, it's the center of the satellite body/bus
        self._rotation_point = np.array([0.0, 0.0, 0.0])

    def _bus(self):
        """ _bus """
        # Satellite bus (satellite body) (Hollow shell - why is it hollow when the outside has no holes - but it's nice code)
        bus_outer_bounds = (-self._body.w/2           , self._body.w/2           , -self._body.d/2           , self._body.d/2           , -self._body.h/2           , self._body.h/2           )
        bus_inner_bounds = (-self._body.w/2+self._wall, self._body.w/2-self._wall, -self._body.d/2+self._wall, self._body.d/2-self._wall, -self._body.h/2+self._wall, self._body.h/2-self._wall)

        bus_outer = pv.Box(bounds=bus_outer_bounds, level=self._u.array)
        bus_inner = pv.Box(bounds=bus_inner_bounds, level=self._u.array)

        bus_outer_surf = bus_outer.extract_surface(algorithm='dataset_surface').triangulate()
        bus_inner_surf = bus_inner.extract_surface(algorithm='dataset_surface').triangulate()

        bus = bus_outer_surf.merge(bus_inner_surf.flip_faces())
        return bus

    def _access(self):
        """ _access ports """
        # Access panels
        access_x_offset = 2.0 * self.CM
        access_z_offset = 2.0 * self.CM

        access1_center = (-access_x_offset             , self._body.d/2, self._body.h/2 - access_z_offset)
        access2_center = (+access_x_offset             , self._body.d/2, self._body.h/2 - access_z_offset)

        w = 3.5 * self.CM
        d = 9.0 * self.MM
        z = 3.0 * self.CM

        access1 = pv.Cube(center=access1_center, x_length=w, y_length=d, z_length=z).triangulate()
        access2 = pv.Cube(center=access2_center, x_length=w, y_length=d, z_length=z).triangulate()

        screwh1_center = (-access_x_offset-1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset-1.20*self.CM)
        screwh2_center = (-access_x_offset+1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset-1.20*self.CM)
        screwh3_center = (-access_x_offset-1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset+1.20*self.CM)
        screwh4_center = (-access_x_offset+1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset+1.20*self.CM)

        screwh1 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh1_center, direction=(0, 1, 0)).triangulate()
        screwh2 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh2_center, direction=(0, 1, 0)).triangulate()
        screwh3 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh3_center, direction=(0, 1, 0)).triangulate()
        screwh4 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh4_center, direction=(0, 1, 0)).triangulate()

        access1 = access1.merge(screwh1).merge(screwh2).merge(screwh3).merge(screwh4)

        screwh1_center = (+access_x_offset-1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset-1.20*self.CM)
        screwh2_center = (+access_x_offset+1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset-1.20*self.CM)
        screwh3_center = (+access_x_offset-1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset+1.20*self.CM)
        screwh4_center = (+access_x_offset+1.45*self.CM, self._body.d/2, self._body.h/2 - access_z_offset+1.20*self.CM)

        screwh1 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh1_center, direction=(0, 1, 0)).triangulate()
        screwh2 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh2_center, direction=(0, 1, 0)).triangulate()
        screwh3 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh3_center, direction=(0, 1, 0)).triangulate()
        screwh4 = pv.Cylinder(radius=0.2*self.CM, height=1.0*self.CM, center=screwh4_center, direction=(0, 1, 0)).triangulate()

        access2 = access2.merge(screwh1).merge(screwh2).merge(screwh3).merge(screwh4)

        return [access1, access2]

    def _camera(self):
        """ _camera """
        # Camera
        camera_sphere = pv.SolidSphere().scale(self._camera_radius).translate(self._camera_center)
        return camera_sphere

    def _lens_barrel(self):
        """ _lens """
        lens_center = (self._camera_center[0], self._camera_center[1] + self._camera_radius * 0.2 + self._lens_length/2, self._camera_center[2])
        # Cylinder is aligned along +Z by default → rotate to +Y
        lens_barrel = pv.Cylinder(center=lens_center, direction=(0, 1, 0), radius=self._lens_radius, height=self._lens_length, resolution=64)   # point along +Y
        return lens_barrel

    def _lens_glass(self):
        """ _lens_glass """
        # Glass lens surface (thin disk)
        lens_center = (self._camera_center[0], self._camera_center[1] + self._camera_radius * 0.2 + self._lens_length, self._camera_center[2])
        lens_glass = pv.Cylinder(center=lens_center, direction=(0, 1, 0), radius=self._lens_radius * 0.95, height=0.8 * self.MM, resolution=64)      # thin glass
        return lens_glass

    def _solar_panels(self):
        """ _solar_panels """
        # Solar panels
        panel_wd = 20 * self.MM
        panel_t = 4 * self.MM
        panel_offset = 1 * self.MM

        neg_y_center = (0                             , -self._body.d/2 - panel_offset, 0)
        pos_x_center = ( self._body.w/2 + panel_offset, 0                             , 0)
        neg_x_center = (-self._body.w/2 - panel_offset, 0                             , 0)

        panel_neg_y = pv.Cube(center=neg_y_center, x_length=self._body.w - panel_wd, y_length=panel_t                , z_length=self._body.h - panel_wd)
        panel_pos_x = pv.Cube(center=pos_x_center, x_length=panel_t                , y_length=self._body.d - panel_wd, z_length=self._body.h - panel_wd)
        panel_neg_x = pv.Cube(center=neg_x_center, x_length=panel_t                , y_length=self._body.d - panel_wd, z_length=self._body.h - panel_wd)
        return [panel_neg_y, panel_pos_x, panel_neg_x]

    def _gps(self):
        """ _gps """
        gps_t = 4.0 * self.MM
        gps_size = 35.0 * self.MM
        gps_height = 4.0 * self.MM

        # GPS patch (center of the top surface)
        gps_body_center =    (0, 0, self._body.h/2 + gps_t)
        gps_antenna_center = (0, 0, self._body.h/2 + gps_t + gps_height)

        gps_body = pv.Cube(center=gps_body_center, x_length=gps_size, y_length=gps_size, z_length=gps_height)
        gps_antenna = pv.Cube(center=gps_antenna_center, x_length=5.0 * self.MM, y_length=5.0 * self.MM, z_length=gps_t)

        gps_body = gps_body.extract_surface(algorithm='dataset_surface').triangulate()
        gps_antenna = gps_antenna.extract_surface(algorithm='dataset_surface').triangulate()

        gps = gps_body.merge(gps_antenna)
        return gps

    def _gps_text(self):
        """ _gps_text """
        # GPS text
        gps_t = 4.0 * self.MM
        gps_height = 4.0 * self.MM

        gps_text_center = (0, 10.0 * self.MM, self._body.h/2 + gps_t + gps_height)
        gps_text = pv.Text3D('GPS', depth=1 * self.MM).scale([5 * self.MM, 5 * self.MM, 5 * self.MM]).rotate_x(90)
        gps_text.points += list(gps_text_center)

        return gps_text

    def _antennas(self):
        """ _antennas """
        # Tape antennas
        def make_antenna(base, direction):
            base = np.array(base)
            direction = np.array(direction, dtype=float)
            direction /= np.linalg.norm(direction)
            end = base + direction * self._antenna_length
            return pv.Tube(pointa=tuple(base), pointb=tuple(end), radius=2.5*self.MM, capping=True, n_sides=16)

        return [
            make_antenna((+25*self.MM, +25*self.MM, self._body.h/2), ( 0.4, 0.4, 1)),
            make_antenna((-25*self.MM, +25*self.MM, self._body.h/2), (-0.4, 0.4, 1))
        ]

    def _rails(self):
        """ _rails """
        # Rails

        rail_z_extra = 3/4 * self.MM

        rail_wd = 4 * self.MM
        rail_offset_w = self._body.w/2 - rail_wd/2
        rail_offset_d = self._body.d/2 - rail_wd/2

        def make_rail(x, y):
            bounds = (
                x - rail_wd                   , x + rail_wd                  ,
                y - rail_wd                   , y + rail_wd                  ,
                -self._body.h/2 - rail_z_extra, self._body.h/2 + rail_z_extra
            )
            return pv.Box(bounds=bounds, level=1)

        return [
            make_rail( rail_offset_w,  rail_offset_d),
            make_rail( rail_offset_w, -rail_offset_d),
            make_rail(-rail_offset_w,  rail_offset_d),
            make_rail(-rail_offset_w, -rail_offset_d),
        ]

    # --------------------------------------------------------
    # Thermal blanket (MLI) gold foil
    # --------------------------------------------------------
    def _mli(self):
        """ _mli """
        mli_t = 1/8 * self.MM    # thickness
        mli_gap = 1/8 * self.MM  # small standoff from structure
        edge_gap = 1 * self.MM

        # needed on pos_z, neg_z, pos_y
        # not needed on neg_y, pos_x, neg_x ('cause solar panels)

        bounds_pos_y = (
            -self._body.w/2 + edge_gap         ,  self._body.w/2 - edge_gap         ,
             self._body.d/2 + mli_gap + mli_t/2,  self._body.d/2 + mli_gap - mli_t/2,
            -self._body.h/2 + edge_gap         ,  self._body.h/2 - edge_gap
        )
        bounds_pos_z = (
            -self._body.w/2 + edge_gap         ,  self._body.w/2 - edge_gap         ,
            -self._body.d/2 + edge_gap         ,  self._body.d/2 - edge_gap         ,
             self._body.h/2 + mli_gap - mli_t/2,  self._body.h/2 + mli_gap + mli_t/2
        )
        bounds_neg_z = (
            -self._body.w/2 + edge_gap         ,  self._body.w/2 - edge_gap         ,
            -self._body.d/2 + edge_gap         ,  self._body.d/2 - edge_gap         ,
            -self._body.h/2 - mli_gap - mli_t/2, -self._body.h/2 - mli_gap + mli_t/2
        )

        level=30

        mli_pos_y = pv.Box(bounds=bounds_pos_y, level=level * max(self._u.d, self._u.h)) #  Y face (front)
        mli_pos_z = pv.Box(bounds=bounds_pos_z, level=level * max(self._u.w, self._u.d)) #  Z face (top)
        mli_neg_z = pv.Box(bounds=bounds_neg_z, level=level * max(self._u.w, self._u.d)) # -Z face (bottom)

        all_mli = [mli_pos_y, mli_pos_z, mli_neg_z]
        for mli in all_mli:
            noise_vector = np.random.rand(mli.n_points, 1) * (mli_t * 0.95)
            # XXX TODO this crinkles every surface - we actually only need to crinkle one surface; but, we do all three
            crinkle_vectors = mli.point_normals * noise_vector
            mli['crinkle'] = crinkle_vectors
            mli.warp_by_vector('crinkle', factor=4.0, inplace=True)
        return all_mli

        # crinkled_mli = [v.warp_by_vector('crinkle', factor=1.0) for v in all_mli]
        # return crinkled_mli

    def _add_parts(self):
        """ _add_parts """
        self.parts = {
            'bus': self._bus(),
            'access': self._access(),
            'camera': self._camera(),
            'barrel': self._lens_barrel(),
            'glass': self._lens_glass(),
            'panels': self._solar_panels(),
            'gps': self._gps(),
            'gps_text': self._gps_text(),
            'antennas': self._antennas(),
            'rails': self._rails(),
            'mli': self._mli(),
        }

    def _add_meshes(self):
        """ _add_meshes """
        # non texture surfaces
        # style='surface' is default
        self._actors = {}
        self._actors['bus']       =  self._plotter.add_mesh(self.parts['bus'],     color='lightgray', smooth_shading=True, specular=0.4, roughness=0.3, metallic=0.6)
        self._actors['camera']    =  self._plotter.add_mesh(self.parts['camera'],  color='black',     smooth_shading=True,                                          )
        self._actors['barrel']    =  self._plotter.add_mesh(self.parts['barrel'],  color='gray',      smooth_shading=True, specular=0.4, roughness=0.3, metallic=0.8)
        self._actors['glass']     =  self._plotter.add_mesh(self.parts['glass'],   color='skyblue',   smooth_shading=True, specular=1.0, roughness=0.0, metallic=0.0, opacity=0.5)
        self._actors['gps']       =  self._plotter.add_mesh(self.parts['gps'],     color='beige',     smooth_shading=True, specular=0.5, roughness=0.4, metallic=0.0)
        self._actors['gps_text']  =  self._plotter.add_mesh(self.parts['gps_text'],color='white',     smooth_shading=True,                                          )
        self._actors['access']    = [self._plotter.add_mesh(a,                     color='lightgray', smooth_shading=True, specular=0.9, roughness=0.5, metallic=0.9) for a in self.parts['access']]
        self._actors['antennas']  = [self._plotter.add_mesh(a,                     color='yellow',    smooth_shading=True,                                          ) for a in self.parts['antennas']]
        self._actors['rails']     = [self._plotter.add_mesh(r,                     color='gray',      smooth_shading=True, specular=0.5, roughness=0.0, metallic=0.0) for r in self.parts['rails']]
        self._actors["mli"]       = [self._plotter.add_mesh(m,                     color='gold',      smooth_shading=True, specular=0.8, roughness=0.1, metallic=0.9) for m in self.parts["mli"]]

        # special case meshes...
        self._add_mesh_bus2()
        self._add_mesh_rails2()
        self._add_mesh_panels()

    def _add_mesh_bus2(self):
        """ _add_mesh_bus2 """
        # edges for bus
        bus_edges = self.parts['bus'].extract_feature_edges(feature_angle=45)
        self._actors['bus2']     =   self._plotter.add_mesh(bus_edges,             color='dimgray',   smooth_shading=True, specular=0.5, roughness=0.0, metallic=0.0, line_width=2)

    def _add_mesh_rails2(self):
        """ _add_mesh_rails2 """
        # edges for rails
        self._actors['rails2'] = []
        for r in self.parts['rails']:
            rails_edges = r.extract_feature_edges(feature_angle=45)
            m =    self._plotter.add_mesh(rails_edges,           color='dimgray',   smooth_shading=True, specular=0.5, roughness=0.0, metallic=0.0, line_width=2)
            self._actors['rails2'].append(m)

    def _add_mesh_panels(self):
        """ _add_mesh_panels """
        # texture solar panels - Generate texture once
        solar_img = self._make_solar_texture()
        solar_tex = self._pil_to_pv_texture(solar_img)
        self._actors["panels"] = []
        for p in self.parts["panels"]:
            actor = self._plotter.add_mesh(p, texture=solar_tex, smooth_shading=True, specular=0.6, roughness=0.2)
            self._actors["panels"].append(actor)

    def _make_solar_texture(self, cells_x=6, cells_y=12, size=512, cell_color=(10, 20, 60), line_color=(180, 180, 200), line_thickness=2):
        """Generate a procedural solar-cell grid texture as a PIL image."""
        img = Image.new("RGB", (size, size), cell_color)
        draw = ImageDraw.Draw(img)

        # Draw vertical grid lines
        for i in range(cells_x + 1):
            x = int(i * size / cells_x)
            draw.rectangle([x - line_thickness//2, 0, x + line_thickness//2, size], fill=line_color)

        # Draw horizontal grid lines
        for j in range(cells_y + 1):
            y = int(j * size / cells_y)
            draw.rectangle([0, y - line_thickness//2, size, y + line_thickness//2], fill=line_color)

        # Optional: slight vignette for realism
        vignette = Image.new("L", (size, size))
        for y in range(size):
            for x in range(size):
                dx = (x - size/2) / (size/2)
                dy = (y - size/2) / (size/2)
                d = math.sqrt(dx*dx + dy*dy)
                vignette.putpixel((x, y), int(255 * min(1, d)))

        img = Image.blend(im1=img, im2=Image.new("RGB", (size, size), (0, 0, 0)), alpha=0.15)
        return img

    def _pil_to_pv_texture(self, pil_img):
        """ _pil_to_pv_texture """
        arr = np.array(pil_img)
        return pv.numpy_to_texture(arr)

    def _centered_transform(self, R, center):
        """ _centered_transform """
        M = np.eye(4)
        M[:3, :3] = R

        # Translate to origin
        T1 = np.eye(4)
        T1[:3, 3] = -np.array(center)

        # Translate back
        T2 = np.eye(4)
        T2[:3, 3] = np.array(center)

        return T2 @ M @ T1

    # XXX TODO  it's actually ['pitch'] ['roll'] ['yaw']
    def apply_orientation(self, roll=0.0, pitch=0.0, yaw=0.0):
        """
        apply_orientation - Rotate the cubesat

        :param roll: Roll.
        :type roll: float
        :param pitch: Pitch.
        :type pitch: float
        :param yaw: Yaw.
        :type yaw: float

        """
        q = self._euler_to_quaternion(roll, pitch, yaw)
        R = self._quaternion_to_matrix(q)

        M_centered = self._rotation_about_point(R)

        # Apply transform to all actors
        for _, item in self._actors.items():
            if isinstance(item, list):
                for actor in item:
                    actor.user_matrix = M_centered
            else:
                item.user_matrix = M_centered

    def _rotation_about_point(self, R):
        """ _rotation_about_point """
        M = np.eye(4)
        M[:3,:3] = R
        M[:3, 3] = (np.eye(3) - R) @ self._rotation_point
        return M

    # ============================================================
    # Quaternion utilities
    # ============================================================

    def _euler_to_quaternion(self, roll, pitch, yaw, degrees=True):
        """ _euler_to_quaternion """
        if degrees:
            roll, pitch, yaw = np.radians([roll, pitch, yaw])

        cr, sr = np.cos(roll/2), np.sin(roll/2)
        cp, sp = np.cos(pitch/2), np.sin(pitch/2)
        cy, sy = np.cos(yaw/2), np.sin(yaw/2)

        w = cr*cp*cy + sr*sp*sy
        x = sr*cp*cy - cr*sp*sy
        y = cr*sp*cy + sr*cp*sy
        z = cr*cp*sy - sr*sp*cy
        return np.array([w, x, y, z])

    def _quaternion_to_matrix(self, q):
        """ _quaternion_to_matrix """
        q = np.array(q, dtype=float)
        q /= np.linalg.norm(q)
        w, x, y, z = q

        return np.array([
            [1 - 2*(y*y + z*z),     2*(x*y - w*z),     2*(x*z + w*y)],
            [    2*(x*y + w*z), 1 - 2*(x*x + z*z),     2*(y*z - w*x)],
            [    2*(x*z - w*y),     2*(y*z + w*x), 1 - 2*(x*x + y*y)],
        ])

class CubesatViewer:
    """ CubesatViewer """

    def __init__(self, u=None, cubesat=None, image_canvas=None, width:int=800, height:int=800):
        """ CubesatViewer """
        if u is not None and cubesat is not None:
            raise ValueError('both u or cubesat value provided') from None
        elif u is not None:
            # we create the Cubesat() here vs externally
            self._cubesat = Cubesat(u=u, width=width, height=height)
        elif cubesat is not None:
            self._cubesat = cubesat
        else:
            raise ValueError('neither u or cubesat value provided') from None
        if image_canvas is None:
            raise ValueError('no image_canvas value provided') from None
        self._image_canvas = image_canvas
        self._width = width
        self._height = height
        # we paint the first time
        self.update_orientation()

    def update_orientation(self, roll:float=0.0, pitch:float=0.0, yaw:float=0.0):
        """
        update_orientation - Rotate the cubesat

        :param roll: Roll.
        :type roll: float
        :param pitch: Pitch.
        :type pitch: float
        :param yaw: Yaw.
        :type yaw: float

        """
        self._cubesat.apply_orientation(roll, pitch, yaw)
        self._render_to_tk()

    def _render_to_tk(self):
        """ _render_to_tk """
        pil_img = Image.fromarray(self._cubesat.render())
        self.current_img = ImageTk.PhotoImage(pil_img)
        # paint new image from pyvista to tk via a label image
        self._image_canvas.configure(image=self.current_img)
