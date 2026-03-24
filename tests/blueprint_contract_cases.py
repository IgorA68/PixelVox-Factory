import os


class BlueprintContractTestMixin:
    blueprint_subdir = None
    build_blueprint_module = None
    blueprint_utils_module = None
    exemplar_blueprint = None
    exemplar_display_name = None
    recommended_dimension_fields = ()

    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.blueprints_dir = os.path.join(self.project_root, self.blueprint_subdir)

    def _blueprint_path(self, file_name):
        return os.path.join(self.blueprints_dir, file_name)

    def _load_blueprint(self, file_name):
        return self.build_blueprint_module.load_blueprint_module(self._blueprint_path(file_name))

    def _find_seeded_blueprint_file(self):
        for file_name in self.blueprint_utils_module.discover_blueprint_files(self.blueprints_dir):
            module = self._load_blueprint(file_name)
            if self.blueprint_utils_module.blueprint_supports_seed(module):
                return file_name, module

        self.fail('Expected at least one blueprint with seed support.')

    def test_resolve_blueprint_path_supports_short_name(self):
        blueprint_name = os.path.splitext(self.exemplar_blueprint)[0]
        resolved_path = self.build_blueprint_module.resolve_blueprint_path(blueprint_name)
        expected_path = self._blueprint_path(self.exemplar_blueprint)
        self.assertEqual(os.path.normcase(os.path.normpath(resolved_path)), os.path.normcase(os.path.normpath(expected_path)))

    def test_all_blueprints_expose_expected_contract(self):
        blueprint_files = self.blueprint_utils_module.discover_blueprint_files(self.blueprints_dir)
        self.assertGreater(len(blueprint_files), 0)

        for file_name in blueprint_files:
            blueprint_path = self._blueprint_path(file_name)
            with self.subTest(blueprint=file_name):
                module = self.build_blueprint_module.load_blueprint_module(blueprint_path)
                self.blueprint_utils_module.validate_blueprint_module(module)

    def test_blueprint_metadata_exposes_display_name_description_and_recommended_size(self):
        fallback_name = os.path.splitext(self.exemplar_blueprint)[0]
        module = self._load_blueprint(self.exemplar_blueprint)
        metadata = self.blueprint_utils_module.get_blueprint_metadata(module, fallback_name=fallback_name)

        self.assertEqual(metadata['display_name'], self.exemplar_display_name)
        self.assertIsInstance(metadata['description'], str)
        self.assertIsInstance(metadata['has_custom_palette'], bool)
        for field_name in self.recommended_dimension_fields:
            self.assertGreater(metadata[field_name], 0)

    def test_discover_blueprint_files_returns_sorted_python_files(self):
        blueprint_files = self.blueprint_utils_module.discover_blueprint_files(self.blueprints_dir)
        self.assertEqual(blueprint_files, sorted(blueprint_files))
        self.assertTrue(all(file_name.endswith('.py') for file_name in blueprint_files))
