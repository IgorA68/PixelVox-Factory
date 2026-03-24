import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from PIL import Image

from vox_art import engine as engine_vox
from palette_utils import MAGICA_DEFAULT_PALETTE


class GeometryHelpersTests(unittest.TestCase):
    def test_is_sphere_handles_inside_and_outside_points(self):
        self.assertTrue(engine_vox.is_sphere(0, 0, 0, 0, 0, 0, 2))
        self.assertTrue(engine_vox.is_sphere(2, 0, 0, 0, 0, 0, 2))
        self.assertFalse(engine_vox.is_sphere(3, 0, 0, 0, 0, 0, 2))

    def test_is_box_includes_boundaries(self):
        self.assertTrue(engine_vox.is_box(1, 1, 1, 1, 1, 1, 3, 3, 3))
        self.assertTrue(engine_vox.is_box(3, 3, 3, 1, 1, 1, 3, 3, 3))
        self.assertFalse(engine_vox.is_box(4, 3, 3, 1, 1, 1, 3, 3, 3))

    def test_is_cylinder_checks_radius_and_height(self):
        self.assertTrue(engine_vox.is_cylinder(0, 1, 2, 0, 0, 1, 0, 3))
        self.assertFalse(engine_vox.is_cylinder(2, 0, 2, 0, 0, 1, 0, 3))
        self.assertFalse(engine_vox.is_cylinder(0, 0, 4, 0, 0, 1, 0, 3))

    def test_is_cone_shrinks_toward_the_tip(self):
        self.assertTrue(engine_vox.is_cone(0, 0, 2, 0, 0, 0, 4, 4))
        self.assertFalse(engine_vox.is_cone(3, 0, 4, 0, 0, 0, 4, 4))
        self.assertTrue(engine_vox.is_cone(0, 0, 4, 0, 0, 0, 4, 4))

    def test_is_capsule_includes_end_caps(self):
        self.assertTrue(engine_vox.is_capsule(0, 0, 2, 0, 0, 2, 4, 1))
        self.assertTrue(engine_vox.is_capsule(0, 0, 1, 0, 0, 2, 4, 1))
        self.assertTrue(engine_vox.is_capsule(0, 0, 5, 0, 0, 2, 4, 1))
        self.assertFalse(engine_vox.is_capsule(2, 0, 2, 0, 0, 2, 4, 1))

    def test_is_torus_matches_ring_shape(self):
        self.assertTrue(engine_vox.is_torus(3, 0, 0, 0, 0, 0, 3, 1))
        self.assertFalse(engine_vox.is_torus(0, 0, 0, 0, 0, 0, 3, 1))

    def test_geometry_helpers_reject_invalid_radii_and_heights(self):
        invalid_calls = [
            (engine_vox.is_sphere, (0, 0, 0, 0, 0, 0, -1), ValueError),
            (engine_vox.is_cylinder, (0, 0, 0, 0, 0, -1, 0, 1), ValueError),
            (engine_vox.is_cone, (0, 0, 0, 0, 0, 0, 0, 1), ValueError),
            (engine_vox.is_cone, (0, 0, 0, 0, 0, 0, 1, -1), ValueError),
            (engine_vox.is_capsule, (0, 0, 0, 0, 0, 0, 1, -1), ValueError),
            (engine_vox.is_torus, (0, 0, 0, 0, 0, 0, -1, 1), ValueError),
            (engine_vox.is_torus, (0, 0, 0, 0, 0, 0, 1, False), TypeError),
        ]

        for func, args, expected_exception in invalid_calls:
            with self.subTest(func=func.__name__, args=args):
                with self.assertRaises(expected_exception):
                    func(*args)


class SaveAsVoxTests(unittest.TestCase):
    def _capture_vox_export(self, fill_func, name='captured', width=1, depth=1, height=1, **kwargs):
        captured = {}

        class FakeWriter:
            def __init__(self, path, vox_data):
                captured['path'] = path
                captured['vox_data'] = vox_data

            def write(self):
                return None

        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with mock.patch.object(engine_vox, 'VoxWriter', FakeWriter):
                    with contextlib.redirect_stdout(io.StringIO()):
                        engine_vox.save_as_vox(name, width, depth, height, fill_func, **kwargs)

        return captured

    def test_save_as_vox_rejects_non_callable_fill_func(self):
        with self.assertRaises(TypeError):
            engine_vox.save_as_vox('bad', 2, 2, 2, None)

    def test_save_as_vox_rejects_invalid_dimensions(self):
        invalid_cases = [
            ('W', 0, 2, 2, ValueError),
            ('D', 2, -1, 2, ValueError),
            ('H', 2, 2, '3', TypeError),
            ('W', True, 2, 2, TypeError),
        ]

        for _, width, depth, height, expected_exception in invalid_cases:
            with self.subTest(width=width, depth=depth, height=height):
                with self.assertRaises(expected_exception):
                    engine_vox.save_as_vox('bad', width, depth, height, lambda *_: 0)

    def test_save_as_vox_rejects_negative_palette_index(self):
        with self.assertRaises(ValueError):
            engine_vox.save_as_vox('bad', 1, 1, 1, lambda *_: -3)

    def test_save_as_vox_maps_truthy_non_int_colors_to_palette_one(self):
        captured = self._capture_vox_export(lambda *_: 'filled', name='truthy')
        voxel = captured['vox_data'].models[0].voxels[0]
        self.assertEqual(voxel.c, 1)

    def test_save_as_vox_skips_falsey_non_int_values(self):
        captured = self._capture_vox_export(lambda *_args: None, name='empty', height=2)
        self.assertEqual(captured['vox_data'].models[0].voxels, [])

    def test_save_as_vox_creates_output_file(self):
        def fill_func(x, y, z, width, depth, height):
            return 5 if (x, y, z) == (0, 0, 0) else 0

        with tempfile.TemporaryDirectory() as temp_dir:
            fake_engine_path = os.path.join(temp_dir, 'vox_art_engine.py')
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(temp_dir, 'models', 'tiny.vox')

            with mock.patch.object(engine_vox, '__file__', fake_engine_path):
                with mock.patch.object(engine_vox, 'PROJECT_ROOT', temp_dir):
                    with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                        with contextlib.redirect_stdout(io.StringIO()):
                            engine_vox.save_as_vox('tiny', 2, 2, 2, fill_func)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)

    def test_save_as_vox_embeds_project_palette_by_default(self):
        captured = self._capture_vox_export(lambda *_: 150, name='palette_default')
        vox_data = captured['vox_data']
        self.assertFalse(vox_data.default_palette)
        self.assertEqual(tuple(vox_data.palette[150]), MAGICA_DEFAULT_PALETTE[150])

    def test_save_as_vox_applies_palette_overrides(self):
        captured = self._capture_vox_export(lambda *_: 150, name='palette_override', palette={150: (1, 2, 3)})
        self.assertEqual(tuple(captured['vox_data'].palette[150]), (1, 2, 3, 255))

    def test_save_as_vox_supports_custom_output_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'custom_models')
            output_path = os.path.join(output_dir, 'custom_vox.vox')

            with contextlib.redirect_stdout(io.StringIO()):
                engine_vox.save_as_vox('custom_vox', 1, 1, 1, lambda *_: 1, output_dir=output_dir)

            self.assertTrue(os.path.exists(output_path))

    def test_save_as_vox_supports_silent_progress_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                engine_vox.save_as_vox('quiet_vox', 1, 1, 1, lambda *_: 1, output_dir=temp_dir, progress=False)

        self.assertEqual(output_buffer.getvalue(), '')


class SavePreviewPngTests(unittest.TestCase):
    def test_save_preview_png_rejects_invalid_scale(self):
        with self.assertRaises(ValueError):
            engine_vox.save_preview_png('bad_preview', 2, 2, 2, lambda *_: 0, scale=0)

    def test_save_preview_png_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            engine_vox.save_preview_png('bad_mode', 2, 2, 2, lambda *_: 0, mode='diagonal')

    def test_resolve_preview_scale_keeps_requested_scale_for_small_model(self):
        self.assertEqual(engine_vox._resolve_preview_scale(64, 64, 64, 6, 'orthographic'), 6)

    def test_resolve_preview_scale_keeps_requested_scale_for_large_top_preview_when_it_fits(self):
        self.assertEqual(engine_vox._resolve_preview_scale(256, 256, 64, 6, 'top'), 6)

    def test_resolve_preview_scale_reduces_large_orthographic_preview(self):
        self.assertEqual(engine_vox._resolve_preview_scale(256, 256, 64, 6, 'orthographic'), 2)

    def test_resolve_preview_scale_reduces_large_isometric_preview(self):
        self.assertEqual(engine_vox._resolve_preview_scale(256, 256, 64, 6, 'isometric'), 3)

    def test_save_preview_png_creates_output_file(self):
        def fill_func(x, y, z, width, depth, height):
            return 5 if (x, y, z) == (0, 0, 0) else 0

        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(fake_models_dir, 'tiny_preview-orthographic.png')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    engine_vox.save_preview_png('tiny_preview', 2, 2, 2, fill_func, scale=4)

            self.assertTrue(os.path.exists(output_path))
            with Image.open(output_path) as image:
                self.assertGreater(image.size[0], 0)
                self.assertGreater(image.size[1], 0)
                self.assertIn(MAGICA_DEFAULT_PALETTE[5], image.getdata())

    def test_save_preview_png_applies_palette_overrides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(fake_models_dir, 'palette_preview-orthographic.png')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    engine_vox.save_preview_png(
                        'palette_preview',
                        1,
                        1,
                        1,
                        lambda *_: 150,
                        palette={150: (1, 2, 3)},
                        scale=4,
                    )

            with Image.open(output_path) as image:
                self.assertIn((1, 2, 3, 255), image.getdata())

    def test_save_preview_png_supports_isometric_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(fake_models_dir, 'iso_preview-isometric.png')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    engine_vox.save_preview_png('iso_preview', 2, 2, 2, lambda *_: 150, scale=2, mode='isometric')

            with Image.open(output_path) as image:
                self.assertGreater(image.size[0], 0)
                self.assertGreater(image.size[1], 0)
                self.assertIn(MAGICA_DEFAULT_PALETTE[150], image.getdata())

    def test_save_preview_png_supports_top_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(fake_models_dir, 'top_preview-top.png')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    engine_vox.save_preview_png('top_preview', 2, 3, 4, lambda *_: 150, scale=4, mode='top')

            with Image.open(output_path) as image:
                self.assertEqual(image.size, (8, 12))
                self.assertIn(MAGICA_DEFAULT_PALETTE[150], image.getdata())

    def test_isometric_preview_scale_stays_reasonable_for_default_house_size(self):
        image = engine_vox._build_isometric_preview([], 64, 64, 64, palette=None, scale=8)

        self.assertEqual(image.size, (1056, 1048))

    def test_preview_dimensions_stay_within_limits_after_auto_scaling(self):
        effective_scale = engine_vox._resolve_preview_scale(256, 256, 64, 6, 'orthographic')
        preview_width, preview_height = engine_vox._get_preview_dimensions(256, 256, 64, effective_scale, 'orthographic')

        self.assertLessEqual(preview_width, engine_vox.MAX_PREVIEW_WIDTH)
        self.assertLessEqual(preview_height, engine_vox.MAX_PREVIEW_HEIGHT)

    def test_save_preview_png_supports_custom_output_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'preview_assets')
            output_path = os.path.join(output_dir, 'custom_preview-orthographic.png')

            with contextlib.redirect_stdout(io.StringIO()):
                engine_vox.save_preview_png('custom_preview', 1, 1, 1, lambda *_: 1, output_dir=output_dir)

            self.assertTrue(os.path.exists(output_path))

    def test_save_preview_png_does_not_duplicate_mode_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_models_dir = os.path.join(temp_dir, 'models')
            output_path = os.path.join(fake_models_dir, 'already-top.png')

            with mock.patch.object(engine_vox, 'MODELS_DIR', fake_models_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    engine_vox.save_preview_png('already-top', 1, 1, 1, lambda *_: 1, mode='top')

            self.assertTrue(os.path.exists(output_path))

    def test_save_preview_png_supports_silent_progress_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                engine_vox.save_preview_png('quiet_preview', 1, 1, 1, lambda *_: 1, output_dir=temp_dir, progress=False)

        self.assertEqual(output_buffer.getvalue(), '')


if __name__ == '__main__':
    unittest.main()