import os
import tempfile
import unittest
from unittest import mock
from PIL import Image

from tests.blueprint_contract_cases import BlueprintContractTestMixin
from pixel_art import blueprint_utils as pixel_blueprint_utils
from pixel_art import build_blueprint as build_pixel_blueprint
from pixel_art.palettes import GEM_PALETTE


class PixelBlueprintContractTests(BlueprintContractTestMixin, unittest.TestCase):
    blueprint_subdir = 'pixel_blueprints'
    build_blueprint_module = build_pixel_blueprint
    blueprint_utils_module = pixel_blueprint_utils
    exemplar_blueprint = 'gem_icon.py'
    exemplar_display_name = 'Gem Icon'
    recommended_dimension_fields = ('recommended_width', 'recommended_height')

    def test_blueprint_supports_seed_is_detected_for_gem_icon(self):
        module = self._load_blueprint('gem_icon.py')
        self.assertTrue(pixel_blueprint_utils.blueprint_supports_seed(module))

    def test_build_fill_func_keeps_seeded_blueprint_deterministic(self):
        module = self._load_blueprint('gem_icon.py')
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

    def test_gem_icon_export_preserves_seeded_pixel_count_and_center_color(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = build_pixel_blueprint.build_blueprint_output(
                'gem_icon',
                seed=7,
                output_dir=temp_dir,
                scale=1,
                quiet=True,
            )

            with Image.open(output_path) as image:
                non_transparent_pixels = sum(1 for pixel in image.getdata() if pixel[3] > 0)
                self.assertEqual(non_transparent_pixels, 43)
                self.assertEqual(image.getpixel((8, 8)), (*GEM_PALETTE[121], 255))

    def test_any_seeded_blueprint_builds_deterministically_with_non_empty_output(self):
        file_name, module = self._find_seeded_blueprint_file()
        width, height = pixel_blueprint_utils.get_blueprint_dimensions(module)
        fill_a = pixel_blueprint_utils.build_fill_func(module, seed=7)
        fill_b = pixel_blueprint_utils.build_fill_func(module, seed=7)
        sample_points = []

        for x in range(0, width, max(1, width // 4)):
            for y in range(0, height, max(1, height // 4)):
                sample_points.append((x, y))

        with self.subTest(blueprint=file_name):
            values_a = [fill_a(x, y, width, height) for x, y in sample_points]
            values_b = [fill_b(x, y, width, height) for x, y in sample_points]
            pixels = build_pixel_blueprint.engine._build_named_pixels('generic_seeded', width, height, fill_a, label='Building', progress=False)

            self.assertEqual(values_a, values_b)
            self.assertGreater(len(pixels), 0)

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