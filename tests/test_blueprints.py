import os
import tempfile
import unittest
from unittest import mock

from vox_art import blueprint_utils
from vox_art import build_blueprint


class BlueprintContractTests(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.blueprints_dir = os.path.join(self.project_root, 'vox_blueprints')

    def test_resolve_blueprint_path_supports_short_name(self):
        resolved_path = build_blueprint.resolve_blueprint_path('house')
        expected_path = os.path.join(self.project_root, 'vox_blueprints', 'house.py')
        self.assertEqual(os.path.normcase(os.path.normpath(resolved_path)), os.path.normcase(os.path.normpath(expected_path)))

    def test_all_blueprints_expose_expected_contract(self):
        blueprint_files = blueprint_utils.discover_blueprint_files(self.blueprints_dir)
        self.assertGreater(len(blueprint_files), 0)

        for file_name in blueprint_files:
            blueprint_path = os.path.join(self.blueprints_dir, file_name)
            with self.subTest(blueprint=file_name):
                module = build_blueprint.load_blueprint_module(blueprint_path)
                blueprint_utils.validate_blueprint_module(module)

    def test_blueprint_metadata_exposes_display_name_description_and_recommended_size(self):
        module = build_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'realistic_tree_vox.py'))
        metadata = blueprint_utils.get_blueprint_metadata(module, fallback_name='realistic_tree_vox')

        self.assertEqual(metadata['display_name'], 'Realistic Tree')
        self.assertIsInstance(metadata['description'], str)
        self.assertGreater(metadata['recommended_width'], 0)
        self.assertGreater(metadata['recommended_depth'], 0)
        self.assertGreater(metadata['recommended_height'], 0)
        self.assertIsInstance(metadata['has_custom_palette'], bool)

    def test_discover_blueprint_files_returns_sorted_python_files(self):
        blueprint_files = blueprint_utils.discover_blueprint_files(self.blueprints_dir)
        self.assertEqual(blueprint_files, sorted(blueprint_files))
        self.assertTrue(all(file_name.endswith('.py') for file_name in blueprint_files))

    def test_blueprint_supports_seed_is_detected_for_realistic_tree(self):
        module = build_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'realistic_tree_vox.py'))
        self.assertTrue(blueprint_utils.blueprint_supports_seed(module))

    def test_build_fill_func_keeps_seeded_blueprint_deterministic(self):
        module = build_blueprint.load_blueprint_module(os.path.join(self.blueprints_dir, 'realistic_tree_vox.py'))
        fill_a = blueprint_utils.build_fill_func(module, seed=7)
        fill_b = blueprint_utils.build_fill_func(module, seed=7)
        fill_c = blueprint_utils.build_fill_func(module, seed=13)

        sample_points = []
        for x in range(20, 80, 6):
            for y in range(20, 80, 6):
                for z in range(50, 118, 8):
                    sample_points.append((x, y, z))

        values_a = [fill_a(x, y, z, 96, 96, 128) for x, y, z in sample_points]
        values_b = [fill_b(x, y, z, 96, 96, 128) for x, y, z in sample_points]
        values_c = [fill_c(x, y, z, 96, 96, 128) for x, y, z in sample_points]

        self.assertEqual(values_a, values_b)
        self.assertNotEqual(values_a, values_c)

    def test_build_showcase_previews_writes_pngs_without_reexporting_vox(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(build_blueprint.engine_vox, 'save_outputs') as save_outputs_mock:
                build_blueprint.build_showcase_previews(preview_scale=3, preview_mode='isometric', preview_output_dir=temp_dir, quiet=True)

        self.assertEqual(save_outputs_mock.call_count, len(build_blueprint.SHOWCASE_PREVIEW_MODELS))
        for call in save_outputs_mock.call_args_list:
            self.assertTrue(call.kwargs['preview_png'])
            self.assertEqual(call.kwargs['preview_scale'], 3)
            self.assertEqual(call.kwargs['preview_mode'], 'isometric')
            self.assertEqual(call.kwargs['preview_output_dir'], temp_dir)
            self.assertFalse(call.kwargs['export_vox'])
            self.assertFalse(call.kwargs['progress'])

    def test_build_blueprint_outputs_supports_preview_only_mode(self):
        with mock.patch.object(build_blueprint.engine_vox, 'save_outputs') as save_outputs_mock:
            build_blueprint.build_blueprint_outputs('house', preview_png=True, preview_mode='isometric', export_vox=False)

        save_outputs_mock.assert_called_once()
        self.assertTrue(save_outputs_mock.call_args.kwargs['preview_png'])
        self.assertEqual(save_outputs_mock.call_args.kwargs['preview_mode'], 'isometric')
        self.assertFalse(save_outputs_mock.call_args.kwargs['export_vox'])

    def test_build_blueprint_outputs_supports_custom_vox_output_directory_and_quiet_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(build_blueprint.engine_vox, 'save_outputs') as save_outputs_mock:
                build_blueprint.build_blueprint_outputs('house', output_dir=temp_dir, quiet=True)

        save_outputs_mock.assert_called_once()
        self.assertEqual(save_outputs_mock.call_args.kwargs['output_dir'], temp_dir)
        self.assertFalse(save_outputs_mock.call_args.kwargs['progress'])


if __name__ == '__main__':
    unittest.main()