from pyvox.models import Model, Size, Vox
from pyvox.writer import VoxWriter

from palette_utils import build_palette


def build_vox_data(width, depth, height, voxels, palette=None, vox_cls=Vox, model_cls=Model, size_cls=Size,
                   build_palette_func=build_palette):
    model = model_cls(size_cls(width, depth, height), voxels)
    return vox_cls([model], palette=build_palette_func(palette))


def write_vox(path, vox_data, writer_cls=VoxWriter):
    writer_cls(path, vox_data).write()
