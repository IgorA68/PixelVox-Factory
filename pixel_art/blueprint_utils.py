import importlib.util
import inspect
import os

from palette_utils import validate_palette_overrides


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PIXEL_BLUEPRINTS_DIR = os.path.join(PROJECT_ROOT, 'pixel_blueprints')
DEFAULT_BLUEPRINT_SIZE = 16


def resolve_blueprint_path(blueprint_arg):
    if os.path.isfile(blueprint_arg):
        return os.path.abspath(blueprint_arg)

    candidate = blueprint_arg
    if not candidate.endswith('.py'):
        candidate = f'{candidate}.py'

    blueprint_path = os.path.join(PIXEL_BLUEPRINTS_DIR, candidate)
    return os.path.abspath(blueprint_path)


def load_blueprint_module(blueprint_path):
    module_name = os.path.splitext(os.path.basename(blueprint_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, blueprint_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load blueprint: {blueprint_path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_blueprint_files(blueprints_dir=PIXEL_BLUEPRINTS_DIR):
    if not os.path.isdir(blueprints_dir):
        return []

    return sorted(
        file_name for file_name in os.listdir(blueprints_dir)
        if file_name.endswith('.py')
    )


def get_blueprint_dimensions(module, fallback=DEFAULT_BLUEPRINT_SIZE):
    return (
        getattr(module, 'DEFAULT_W', fallback),
        getattr(module, 'DEFAULT_H', fallback),
    )


def get_blueprint_metadata(module, fallback_name=None, fallback=DEFAULT_BLUEPRINT_SIZE):
    default_width, default_height = get_blueprint_dimensions(module, fallback)
    palette_overrides = get_blueprint_palette_overrides(module)
    metadata = {
        'display_name': getattr(module, 'BLUEPRINT_DISPLAY_NAME', fallback_name or module.__name__),
        'description': getattr(module, 'BLUEPRINT_DESCRIPTION', ''),
        'recommended_width': getattr(module, 'RECOMMENDED_W', default_width),
        'recommended_height': getattr(module, 'RECOMMENDED_H', default_height),
        'supports_seed': blueprint_supports_seed(module),
        'has_custom_palette': bool(palette_overrides),
    }
    validate_blueprint_metadata(metadata)
    return metadata


def validate_blueprint_metadata(metadata):
    if not isinstance(metadata['display_name'], str) or not metadata['display_name'].strip():
        raise ValueError('BLUEPRINT_DISPLAY_NAME must be a non-empty string.')

    if not isinstance(metadata['description'], str):
        raise ValueError('BLUEPRINT_DESCRIPTION must be a string.')

    for field_name in ('recommended_width', 'recommended_height'):
        value = metadata[field_name]
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{field_name} must be a positive integer, got {value!r}')

    if not isinstance(metadata['supports_seed'], bool):
        raise ValueError('supports_seed metadata must be boolean.')

    if not isinstance(metadata['has_custom_palette'], bool):
        raise ValueError('has_custom_palette metadata must be boolean.')


def get_blueprint_palette_overrides(module):
    palette_overrides = getattr(module, 'BLUEPRINT_PALETTE_OVERRIDES', None)
    validate_palette_overrides(palette_overrides)
    return palette_overrides


def blueprint_supports_seed(module):
    make_image = getattr(module, 'make_image', None)
    if not callable(make_image):
        return False

    signature = inspect.signature(make_image)
    parameters = list(signature.parameters.values())

    if any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in parameters):
        return True

    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters):
        return True

    if any(param.name == 'seed' for param in parameters):
        return True

    return len(parameters) >= 5


def build_fill_func(module, seed=None):
    validate_blueprint_module(module)

    if seed is None or not blueprint_supports_seed(module):
        return module.make_image

    signature = inspect.signature(module.make_image)
    parameters = list(signature.parameters.values())
    accepts_keyword_seed = any(param.name == 'seed' for param in parameters)
    accepts_var_keyword = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters)

    if accepts_keyword_seed or accepts_var_keyword:
        def fill_func(x, y, width, height):
            return module.make_image(x, y, width, height, seed=seed)

        return fill_func

    def fill_func(x, y, width, height):
        return module.make_image(x, y, width, height, seed)

    return fill_func


def validate_blueprint_module(module):
    if not callable(getattr(module, 'make_image', None)):
        raise AttributeError('Blueprint must define make_image(x, y, W, H) with an optional seed parameter only as a backward-compatible extension.')

    for attr_name in ('DEFAULT_W', 'DEFAULT_H'):
        if not hasattr(module, attr_name):
            continue

        value = getattr(module, attr_name)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'{attr_name} must be a positive integer, got {value!r}')

    get_blueprint_palette_overrides(module)
    get_blueprint_metadata(module)