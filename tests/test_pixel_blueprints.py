import os
import tempfile
import unittest
from unittest import mock
from PIL import Image

from pixel_art import blueprint_utils as pixel_blueprint_utils
from pixel_art import build_blueprint as build_pixel_blueprint


class PixelBlueprintContractTests(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.blueprints_dir = os.path.join(self.project_root, 'pixel_blueprints')

    def test_resolve_blueprint_path_supports_short_name(self):
        resolved_path = build_pixel_blueprint.resolve_blueprint_path('gem_icon')
        expected_path = os.path.join(self.project_root, 'pixel_blueprints', 'gem_icon.py')
        self.assertEqual(resolved_path, expected_path)

    def test_all_blueprints_expose_expected_contract(self):
        blueprint_files = pixel_blueprint_utils.discover_blueprint_files(self.blueprints_dir)
        self.assertGreater(len(blueprint_files), 0)

        for file_name in blueprint_files:
            blueprint_path = os.path.join(self.blueprints_dir, file_name)
            with self.subTest(blueprint=file_name):
                module = build_pixel_blueprint.load_blueprint_module(blueprint_path)
                pixel_blueprint_utils.validate_blueprint_module(module)

    def test_blueprint_metadata_exposes_display_name_description_and_recommended_size(self):
        module = build_pixel_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'gem_icon.py'))
        metadata = pixel_blueprint_utils.get_blueprint_metadata(module, fallback_name='gem_icon')

        self.assertEqual(metadata['display_name'], 'Gem Icon')
        self.assertIsInstance(metadata['description'], str)
        self.assertGreater(metadata['recommended_width'], 0)
        self.assertGreater(metadata['recommended_height'], 0)
        self.assertIsInstance(metadata['has_custom_palette'], bool)

    def test_discover_blueprint_files_returns_sorted_python_files(self):
        blueprint_files = pixel_blueprint_utils.discover_blueprint_files(self.blueprints_dir)
        self.assertEqual(blueprint_files, sorted(blueprint_files))
        self.assertTrue(all(file_name.endswith('.py') for file_name in blueprint_files))

    def test_blueprint_supports_seed_is_detected_for_gem_icon(self):
        module = build_pixel_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'gem_icon.py'))
        self.assertTrue(pixel_blueprint_utils.blueprint_supports_seed(module))

    def test_build_fill_func_keeps_seeded_blueprint_deterministic(self):
        module = build_pixel_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'gem_icon.py'))
        fill_a = pixel_blueprint_utils.build_fill_func(module, seed=7)
        fill_b = pixel_blueprint_utils.build_fill_func(module, seed=7)
        fill_c = pixel_blueprint_utils.build_fill_func(module, seed=13)

        sample_points = []
        for x in range(16):
            for y in range(16):
                sample_points.append((x, y))

        values_a = [fill_a(x, y, 16, 16) for x, y in sample_points]
        values_b = [fill_b(x, y, 16, 16) for x, y in sample_points]
        values_c = [fill_c(x, y, 16, 16) for x, y in sample_points]

        self.assertEqual(values_a, values_b)
        self.assertNotEqual(values_a, values_c)

    def test_build_blueprint_output_supports_custom_output_directory_and_quiet_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(build_pixel_blueprint.engine, 'save_as_png') as save_as_png_mock:
                build_pixel_blueprint.build_blueprint_output('gem_icon', output_dir=temp_dir, quiet=True)

        save_as_png_mock.assert_called_once()
        self.assertEqual(save_as_png_mock.call_args.kwargs['output_dir'], temp_dir)
        self.assertFalse(save_as_png_mock.call_args.kwargs['progress'])

    def test_build_showcase_pixel_outputs_writes_curated_pngs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(build_pixel_blueprint, 'build_blueprint_output') as build_output_mock:
                build_pixel_blueprint.build_showcase_pixel_outputs(output_dir=temp_dir, quiet=True)

        self.assertEqual(build_output_mock.call_count, len(build_pixel_blueprint.SHOWCASE_PIXEL_BLUEPRINTS))
        for call, entry in zip(build_output_mock.call_args_list, build_pixel_blueprint.SHOWCASE_PIXEL_BLUEPRINTS):
            self.assertEqual(call.args[0], entry['blueprint'])
            self.assertEqual(call.kwargs['output_dir'], temp_dir)
            self.assertEqual(call.kwargs['quiet'], True)
            self.assertEqual(call.kwargs['scale'], entry.get('scale', 8))
            self.assertEqual(call.kwargs['output_name'], entry['output_name'])
            self.assertEqual(call.kwargs['seed'], entry.get('seed'))

    def test_showcase_pixel_blueprints_export_at_native_and_upscaled_sizes(self):
        showcase_blueprints = [
            ('gem_icon', 1),
            ('potion_icon', 1),
            ('grass_tile', 1),
            ('crate_prop', 4),
            ('tiny_face_avatar', 3),
            ('bush_prop', 4),
            ('stone_floor_tile', 2),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            for blueprint_name, scale in showcase_blueprints:
                with self.subTest(blueprint=blueprint_name, scale=scale):
                    output_path = build_pixel_blueprint.build_blueprint_output(
                        blueprint_name,
                        seed=7,
                        output_dir=temp_dir,
                        scale=scale,
                        quiet=True,
                    )

                    self.assertTrue(os.path.exists(output_path))
                    with Image.open(output_path) as image:
                        self.assertGreater(image.size[0], 0)
                        self.assertGreater(image.size[1], 0)


if __name__ == '__main__':
    unittest.main()