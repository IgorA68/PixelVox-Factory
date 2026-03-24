import contextlib
import io
import os
import tempfile
import unittest

from PIL import Image

from pixel_art import engine as engine_pixel
from palette_utils import MAGICA_DEFAULT_PALETTE


class GeometryHelpersTests(unittest.TestCase):
    def test_is_rect_includes_boundaries(self):
        self.assertTrue(engine_pixel.is_rect(1, 1, 1, 1, 3, 3))
        self.assertTrue(engine_pixel.is_rect(3, 3, 1, 1, 3, 3))
        self.assertFalse(engine_pixel.is_rect(4, 3, 1, 1, 3, 3))

    def test_is_rect_outline_handles_border_and_thickness(self):
        self.assertTrue(engine_pixel.is_rect_outline(1, 1, 1, 1, 5, 5))
        self.assertFalse(engine_pixel.is_rect_outline(3, 3, 1, 1, 5, 5))
        self.assertTrue(engine_pixel.is_rect_outline(2, 2, 1, 1, 5, 5, thickness=2))

    def test_is_line_handles_horizontal_diagonal_and_thickness(self):
        self.assertTrue(engine_pixel.is_line(2, 0, 0, 0, 4, 0))
        self.assertFalse(engine_pixel.is_line(2, 1, 0, 0, 4, 0))
        self.assertTrue(engine_pixel.is_line(2, 1, 0, 0, 4, 0, thickness=2))
        self.assertTrue(engine_pixel.is_line(1, 1, 0, 0, 3, 3))

    def test_is_polyline_handles_open_and_closed_shapes(self):
        vertices = [(0, 0), (3, 0), (3, 3)]

        self.assertTrue(engine_pixel.is_polyline(1, 0, vertices))
        self.assertTrue(engine_pixel.is_polyline(3, 2, vertices))
        self.assertFalse(engine_pixel.is_polyline(0, 2, vertices))
        self.assertTrue(engine_pixel.is_polyline(1, 1, vertices, closed=True))

    def test_is_circle_handles_inside_and_outside_points(self):
        self.assertTrue(engine_pixel.is_circle(0, 0, 0, 0, 2))
        self.assertTrue(engine_pixel.is_circle(2, 0, 0, 0, 2))
        self.assertFalse(engine_pixel.is_circle(3, 0, 0, 0, 2))

    def test_is_circle_outline_handles_ring_and_thickness(self):
        self.assertTrue(engine_pixel.is_circle_outline(2, 0, 0, 0, 2))
        self.assertFalse(engine_pixel.is_circle_outline(0, 0, 0, 0, 3))
        self.assertTrue(engine_pixel.is_circle_outline(1, 0, 0, 0, 2, thickness=2))

    def test_is_ellipse_handles_inside_and_outside_points(self):
        self.assertTrue(engine_pixel.is_ellipse(0, 0, 0, 0, 2, 3))
        self.assertFalse(engine_pixel.is_ellipse(3, 0, 0, 0, 2, 3))

    def test_is_ellipse_outline_handles_border_and_thickness(self):
        self.assertTrue(engine_pixel.is_ellipse_outline(0, 4, 0, 0, 3, 4))
        self.assertFalse(engine_pixel.is_ellipse_outline(0, 0, 0, 0, 3, 4))
        self.assertTrue(engine_pixel.is_ellipse_outline(1, 0, 0, 0, 2, 2, thickness=2))

    def test_is_diamond_handles_inside_and_outside_points(self):
        self.assertTrue(engine_pixel.is_diamond(0, 0, 0, 0, 2, 2))
        self.assertTrue(engine_pixel.is_diamond(2, 0, 0, 0, 2, 2))
        self.assertFalse(engine_pixel.is_diamond(2, 2, 0, 0, 2, 2))

    def test_is_diamond_outline_handles_border_and_thickness(self):
        self.assertTrue(engine_pixel.is_diamond_outline(2, 0, 0, 0, 2, 2))
        self.assertFalse(engine_pixel.is_diamond_outline(0, 0, 0, 0, 3, 3))
        self.assertTrue(engine_pixel.is_diamond_outline(1, 0, 0, 0, 2, 2, thickness=2))

    def test_is_polygon_handles_convex_and_concave_shapes(self):
        square = [(1, 1), (5, 1), (5, 5), (1, 5)]
        concave = [(1, 1), (5, 1), (5, 3), (3, 3), (3, 5), (1, 5)]

        self.assertTrue(engine_pixel.is_polygon(3, 3, square))
        self.assertTrue(engine_pixel.is_polygon(1, 3, square))
        self.assertFalse(engine_pixel.is_polygon(6, 3, square))
        self.assertTrue(engine_pixel.is_polygon(2, 4, concave))
        self.assertFalse(engine_pixel.is_polygon(4, 4, concave))

    def test_is_polygon_outline_traces_closed_polygon_edges(self):
        triangle = [(1, 1), (5, 1), (3, 5)]

        self.assertTrue(engine_pixel.is_polygon_outline(3, 1, triangle))
        self.assertTrue(engine_pixel.is_polygon_outline(2, 3, triangle, thickness=2))
        self.assertFalse(engine_pixel.is_polygon_outline(3, 2, triangle))

    def test_geometry_helpers_reject_invalid_radii(self):
        invalid_calls = [
            (engine_pixel.is_circle, (0, 0, 0, 0, -1), ValueError),
            (engine_pixel.is_ellipse, (0, 0, 0, 0, -1, 1), ValueError),
            (engine_pixel.is_diamond, (0, 0, 0, 0, 1, False), TypeError),
            (engine_pixel.is_rect_outline, (0, 0, 0, 0, 2, 2, 0), ValueError),
            (engine_pixel.is_line, (0, 0, 0, 0, 1, 1, 0), ValueError),
            (engine_pixel.is_polyline, (0, 0, [(0, 0)], 1), ValueError),
            (engine_pixel.is_polyline, (0, 0, [(0, 0), (1, 1)], 1, 'yes'), TypeError),
            (engine_pixel.is_circle_outline, (0, 0, 0, 0, 2, 0), ValueError),
            (engine_pixel.is_ellipse_outline, (0, 0, 0, 0, 2, 2, 0), ValueError),
            (engine_pixel.is_diamond_outline, (0, 0, 0, 0, 2, 2, 0), ValueError),
            (engine_pixel.is_polygon, (0, 0, [(0, 0), (1, 1)]), ValueError),
            (engine_pixel.is_polygon_outline, (0, 0, [(0, 0), (1, 1)]), ValueError),
        ]

        for func, args, expected_exception in invalid_calls:
            with self.subTest(func=func.__name__, args=args):
                with self.assertRaises(expected_exception):
                    func(*args)


class SaveAsPngTests(unittest.TestCase):
    def _render_png(self, fill_func, width=1, height=1, name='rendered', **kwargs):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = engine_pixel.save_as_png(
                name,
                width,
                height,
                fill_func,
                output_dir=temp_dir,
                progress=False,
                **kwargs,
            )

            with Image.open(output_path) as image:
                return image.copy()

    def test_save_as_png_rejects_non_callable_fill_func(self):
        with self.assertRaises(TypeError):
            engine_pixel.save_as_png('bad', 2, 2, None)

    def test_save_as_png_rejects_invalid_dimensions(self):
        invalid_cases = [
            (0, 2, ValueError),
            (2, -1, ValueError),
            ('2', 2, TypeError),
            (True, 2, TypeError),
        ]

        for width, height, expected_exception in invalid_cases:
            with self.subTest(width=width, height=height):
                with self.assertRaises(expected_exception):
                    engine_pixel.save_as_png('bad', width, height, lambda *_: 0)

    def test_save_as_png_rejects_negative_palette_index(self):
        with self.assertRaises(ValueError):
            engine_pixel.save_as_png('bad', 1, 1, lambda *_: -3)

    def test_save_as_png_rejects_invalid_scale(self):
        with self.assertRaises(ValueError):
            engine_pixel.save_as_png('bad', 2, 2, lambda *_: 0, scale=0)

    def test_save_as_png_maps_truthy_non_int_colors_to_palette_one(self):
        image = self._render_png(lambda *_: 'filled', name='truthy')
        self.assertEqual(image.getpixel((0, 0)), MAGICA_DEFAULT_PALETTE[1])

    def test_save_as_png_skips_falsey_non_int_values(self):
        image = self._render_png(lambda *_: None, name='empty')
        self.assertEqual(image.getpixel((0, 0))[3], 0)

    def test_save_as_png_creates_output_file_with_scaled_dimensions(self):
        def fill_func(x, y, width, height):
            return 5 if (x, y) == (0, 0) else 0

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = engine_pixel.save_as_png('tiny_pixel', 2, 3, fill_func, scale=4, output_dir=temp_dir, progress=False)

            self.assertTrue(os.path.exists(output_path))
            with Image.open(output_path) as image:
                self.assertEqual(image.size, (8, 12))
                self.assertIn(MAGICA_DEFAULT_PALETTE[5], image.getdata())

    def test_save_as_png_applies_palette_overrides(self):
        image = self._render_png(lambda *_: 150, name='palette_override', palette={150: (1, 2, 3)})
        self.assertEqual(image.getpixel((0, 0)), (1, 2, 3, 255))

    def test_save_as_png_supports_custom_output_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'images')
            output_path = os.path.join(output_dir, 'custom.png')

            with contextlib.redirect_stdout(io.StringIO()):
                engine_pixel.save_as_png('custom', 1, 1, lambda *_: 1, output_dir=output_dir)

            self.assertTrue(os.path.exists(output_path))

    def test_save_as_png_supports_silent_progress_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                engine_pixel.save_as_png('quiet_png', 1, 1, lambda *_: 1, output_dir=temp_dir, progress=False)

        self.assertEqual(output_buffer.getvalue(), '')

    def test_save_as_png_supports_solid_background(self):
        image = self._render_png(
            lambda x, y, *_: 1 if (x, y) == (0, 0) else 0,
            width=2,
            height=2,
            name='background',
            background=(10, 20, 30),
            scale=1,
        )
        self.assertEqual(image.getpixel((1, 1)), (10, 20, 30, 255))


if __name__ == '__main__':
    unittest.main()