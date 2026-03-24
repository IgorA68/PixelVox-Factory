import os
import tempfile
import unittest
from unittest import mock

from tests.blueprint_contract_cases import BlueprintContractTestMixin
from vox_art import blueprint_utils
from vox_art import build_blueprint


class BlueprintContractTests(BlueprintContractTestMixin, unittest.TestCase):
    blueprint_subdir = 'vox_blueprints'
    build_blueprint_module = build_blueprint
    blueprint_utils_module = blueprint_utils
    exemplar_blueprint = 'realistic_tree_vox.py'
    exemplar_display_name = 'Realistic Tree'
    recommended_dimension_fields = ('recommended_width', 'recommended_depth', 'recommended_height')

    def test_blueprint_supports_seed_is_detected_for_realistic_tree(self):
        module = self._load_blueprint('realistic_tree_vox.py')
        self.assertTrue(blueprint_utils.blueprint_supports_seed(module))

    def test_build_fill_func_keeps_seeded_blueprint_deterministic(self):
        module = self._load_blueprint('realistic_tree_vox.py')
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

    def test_realistic_tree_seeded_build_context_generates_expected_voxel_count_and_trunk_color(self):
        _, width, depth, height, fill_func, _ = build_blueprint._resolve_blueprint_build_context('realistic_tree_vox', seed=7)

        voxels = build_blueprint.engine_vox._build_voxel_list(width, depth, height, fill_func, progress=False)

        self.assertEqual(len(voxels), 113130)
        self.assertTrue(any((voxel.x, voxel.y, voxel.z, voxel.c) == (48, 48, 10, 131) for voxel in voxels))
        self.assertFalse(any((voxel.x, voxel.y, voxel.z) == (60, 48, 80) for voxel in voxels))

    def test_any_seeded_blueprint_builds_deterministically_with_non_empty_output(self):
        file_name, module = self._find_seeded_blueprint_file()
        width, depth, height = blueprint_utils.get_blueprint_dimensions(module)
        fill_a = blueprint_utils.build_fill_func(module, seed=7)
        fill_b = blueprint_utils.build_fill_func(module, seed=7)
        sample_points = []

        for x in range(0, width, max(1, width // 4)):
            for y in range(0, depth, max(1, depth // 4)):
                for z in range(0, height, max(1, height // 4)):
                    sample_points.append((x, y, z))

        with self.subTest(blueprint=file_name):
            values_a = [fill_a(x, y, z, width, depth, height) for x, y, z in sample_points]
            values_b = [fill_b(x, y, z, width, depth, height) for x, y, z in sample_points]
            voxels = build_blueprint.engine_vox._build_voxel_list(width, depth, height, fill_a, progress=False)

            self.assertEqual(values_a, values_b)
            self.assertGreater(len(voxels), 0)

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