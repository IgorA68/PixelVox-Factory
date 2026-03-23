import json
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from vox_art.blueprint_utils import BLUEPRINTS_DIR
from vox_art.blueprint_utils import PROJECT_ROOT
from vox_art.blueprint_utils import discover_blueprint_files
from vox_art.blueprint_utils import get_blueprint_metadata
from vox_art.blueprint_utils import load_blueprint_module
from vox_art.blueprint_utils import read_blueprint_defaults
from vox_art.blueprint_utils import validate_blueprint_module


running_processes = []
current_loaded_file = None
blueprint_entries = {}
MODELS_DIR = os.path.join(PROJECT_ROOT, 'vox_models')
GUI_STATE_PATH = os.path.join(PROJECT_ROOT, '.vox_gui_state.json')
DEFAULT_WINDOW_GEOMETRY = '760x430'
DEFAULT_PREVIEW_SCALE = '6'
DEFAULT_PREVIEW_MODE = 'orthographic'


def load_window_state():
    if not os.path.exists(GUI_STATE_PATH):
        return {
            'geometry': DEFAULT_WINDOW_GEOMETRY,
            'zoomed': False,
            'preview_enabled': True,
            'preview_only': False,
            'preview_mode': DEFAULT_PREVIEW_MODE,
            'preview_scale': DEFAULT_PREVIEW_SCALE,
        }

    try:
        with open(GUI_STATE_PATH, 'r', encoding='utf-8') as handle:
            state = json.load(handle)
    except (OSError, ValueError, TypeError):
        return {
            'geometry': DEFAULT_WINDOW_GEOMETRY,
            'zoomed': False,
            'preview_enabled': True,
            'preview_only': False,
            'preview_mode': DEFAULT_PREVIEW_MODE,
            'preview_scale': DEFAULT_PREVIEW_SCALE,
        }

    geometry = state.get('geometry', DEFAULT_WINDOW_GEOMETRY)
    zoomed = bool(state.get('zoomed', False))
    preview_enabled = bool(state.get('preview_enabled', True))
    preview_only = bool(state.get('preview_only', False))
    preview_mode = state.get('preview_mode', DEFAULT_PREVIEW_MODE)
    preview_scale = str(state.get('preview_scale', DEFAULT_PREVIEW_SCALE))

    if not isinstance(geometry, str) or not re.fullmatch(r'\d+x\d+([+-]\d+){2}', geometry):
        geometry = DEFAULT_WINDOW_GEOMETRY

    if preview_mode not in ('orthographic', 'isometric', 'both', 'top'):
        preview_mode = DEFAULT_PREVIEW_MODE

    if not re.fullmatch(r'\d+', preview_scale) or int(preview_scale) <= 0:
        preview_scale = DEFAULT_PREVIEW_SCALE

    return {
        'geometry': geometry,
        'zoomed': zoomed,
        'preview_enabled': preview_enabled,
        'preview_only': preview_only,
        'preview_mode': preview_mode,
        'preview_scale': preview_scale,
    }


def save_window_state(root_window):
    state = {
        'geometry': root_window.geometry(),
        'zoomed': root_window.state() == 'zoomed',
        'preview_enabled': bool(preview_enabled_var.get()),
        'preview_only': bool(preview_only_var.get()),
        'preview_mode': preview_mode_var.get(),
        'preview_scale': ent_preview_scale.get().strip() or DEFAULT_PREVIEW_SCALE,
    }

    try:
        with open(GUI_STATE_PATH, 'w', encoding='utf-8') as handle:
            json.dump(state, handle, indent=2)
    except OSError:
        pass


def resolve_python_executable():
    python_exe = sys.executable or 'python'
    if os.path.basename(python_exe).lower() == 'pythonw.exe':
        console_python = os.path.join(os.path.dirname(python_exe), 'python.exe')
        if os.path.exists(console_python):
            return console_python
    return python_exe


def get_dimensions_from_file(file_path):
    try:
        return read_blueprint_defaults(file_path)
    except OSError:
        return {'W': 64, 'D': 64, 'H': 64}


def parse_positive_dimension(value, label):
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise ValueError(f'{label} must be an integer') from exc

    if parsed_value <= 0:
        raise ValueError(f'{label} must be greater than zero')

    return parsed_value


def parse_optional_seed(value):
    cleaned_value = value.strip()
    if not cleaned_value:
        return None

    try:
        return int(cleaned_value)
    except ValueError as exc:
        raise ValueError('Seed must be an integer') from exc


def sanitize_output_name(value, fallback_name):
    cleaned_value = re.sub(r'[^A-Za-z0-9_-]+', '_', value.strip())
    return cleaned_value or fallback_name


def parse_preview_scale(value):
    return parse_positive_dimension(value, 'Preview scale')


def set_info_description(text):
    txt_description.config(state=tk.NORMAL)
    txt_description.delete('1.0', tk.END)
    txt_description.insert('1.0', text)
    txt_description.config(state=tk.DISABLED)


def validate_blueprint(script_path):
    try:
        module = load_blueprint_module(script_path)
        validate_blueprint_module(module)
    except SyntaxError as exc:
        line_info = f'Line {exc.lineno}' if exc.lineno else 'Unknown line'
        code_line = exc.text.strip() if exc.text else ''
        details = f'{line_info}\n\n{code_line}\n\n{exc.msg}' if code_line else f'{line_info}\n\n{exc.msg}'
        messagebox.showerror('Blueprint error', f'Could not parse {os.path.basename(script_path)}.\n\n{details}')
        return False
    except (AttributeError, ValueError) as exc:
        messagebox.showerror('Blueprint error', f'{os.path.basename(script_path)} does not match the blueprint contract.\n\n{exc}')
        return False
    except Exception as exc:
        messagebox.showerror('Blueprint error', f'Could not load {os.path.basename(script_path)}.\n\n{type(exc).__name__}: {exc}')
        return False

    return True


def ensure_blueprints_dir():
    if os.path.isdir(BLUEPRINTS_DIR):
        return True

    messagebox.showerror('Project error', f'The vox_blueprints folder was not found:\n{BLUEPRINTS_DIR}')
    return False


def open_models_folder():
    if not os.path.isdir(MODELS_DIR):
        messagebox.showinfo('Output folder', f'The output folder does not exist yet. It will be created after the first successful build and will contain generated .vox models plus PNG previews.\n\nPath:\n{MODELS_DIR}')
        return

    os.startfile(MODELS_DIR)


def launch_build(script_path, width, depth, height, output_name, seed=None, preview_enabled=False,
                 preview_scale=8, preview_mode='orthographic', preview_only=False):
    python_exe = resolve_python_executable()
    command = [
        python_exe,
        '-m', 'vox_art.build_blueprint',
        script_path,
        '--width', str(width),
        '--depth', str(depth),
        '--height', str(height),
        '--output-name', output_name,
    ]
    if seed is not None:
        command.extend(['--seed', str(seed)])
    if preview_only:
        command.extend(['--preview-only', '--preview-scale', str(preview_scale), '--preview-mode', preview_mode])
    elif preview_enabled:
        command.extend(['--preview-png', '--preview-scale', str(preview_scale), '--preview-mode', preview_mode])

    try:
        proc = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=PROJECT_ROOT)
        running_processes.append(proc)
    except Exception as exc:
        messagebox.showerror('Launch error', f'Could not start the build process:\n{exc}')


def refresh():
    global current_loaded_file
    global blueprint_entries

    listbox.delete(0, tk.END)
    blueprint_entries = {}
    if not ensure_blueprints_dir():
        current_loaded_file = None
        info_name_var.set('No blueprint selected')
        set_info_description('')
        info_seed_var.set('Seeded variants: unavailable')
        info_palette_var.set('Embedded palette: unavailable')
        return

    blueprints = discover_blueprint_files(BLUEPRINTS_DIR)
    for item in blueprints:
        script_path = os.path.join(BLUEPRINTS_DIR, item)
        display_name = os.path.splitext(item)[0]
        description = ''
        try:
            module = load_blueprint_module(script_path)
            metadata = get_blueprint_metadata(module, fallback_name=display_name)
            display_name = metadata['display_name']
            description = metadata['description']
        except Exception:
            metadata = None

        blueprint_entries[item] = {
            'path': script_path,
            'display_name': display_name,
            'description': description,
            'metadata': metadata,
        }
        listbox.insert(tk.END, f'{display_name}  [{item}]')

    if not blueprints:
        messagebox.showinfo('No blueprints found', f'The vox_blueprints folder does not contain any .py files.\n\nPath:\n{BLUEPRINTS_DIR}')


def on_select(evt):
    global current_loaded_file
    selection = evt.widget.curselection()
    if not selection:
        return

    selected_index = selection[0]
    selected_file = discover_blueprint_files(BLUEPRINTS_DIR)[selected_index]
    if selected_file == current_loaded_file:
        return

    current_loaded_file = selected_file
    script_path = os.path.join(BLUEPRINTS_DIR, selected_file)
    entry = blueprint_entries.get(selected_file, {})
    metadata = entry.get('metadata') or {}
    dims = get_dimensions_from_file(script_path)
    model_name = os.path.splitext(selected_file)[0]

    recommended_w = metadata.get('recommended_width', dims['W'])
    recommended_d = metadata.get('recommended_depth', dims['D'])
    recommended_h = metadata.get('recommended_height', dims['H'])
    info_name_var.set(entry.get('display_name', model_name))
    set_info_description(entry.get('description', ''))
    info_seed_var.set('Seeded variants: supported' if metadata.get('supports_seed') else 'Seeded variants: not supported')
    info_palette_var.set('Embedded palette: custom' if metadata.get('has_custom_palette') else 'Embedded palette: MagicaVoxel pal0 baseline')

    ent_w.delete(0, tk.END)
    ent_w.insert(0, str(recommended_w))
    ent_d.delete(0, tk.END)
    ent_d.insert(0, str(recommended_d))
    ent_h.delete(0, tk.END)
    ent_h.insert(0, str(recommended_h))
    ent_seed.delete(0, tk.END)
    ent_output.delete(0, tk.END)
    ent_output.insert(0, model_name)


def run_selected():
    if not ensure_blueprints_dir():
        return

    selection = listbox.curselection()
    blueprint_files = discover_blueprint_files(BLUEPRINTS_DIR)
    script_name = blueprint_files[selection[0]] if selection else current_loaded_file
    if not script_name:
        messagebox.showwarning('No selection', 'Select a blueprint first.')
        return

    model_name = os.path.splitext(script_name)[0]
    script_path = os.path.join(BLUEPRINTS_DIR, script_name)
    output_name = sanitize_output_name(ent_output.get(), model_name)

    if not validate_blueprint(script_path):
        return

    try:
        width = parse_positive_dimension(ent_w.get(), 'Width')
        depth = parse_positive_dimension(ent_d.get(), 'Depth')
        height = parse_positive_dimension(ent_h.get(), 'Height')
        seed = parse_optional_seed(ent_seed.get())
        preview_scale = parse_preview_scale(ent_preview_scale.get())
    except ValueError as exc:
        messagebox.showwarning('Invalid dimensions', str(exc))
        return

    if seed is not None and output_name == model_name:
        output_name = f'{model_name}_seed_{seed}'

    launch_build(
        script_path,
        width,
        depth,
        height,
        output_name,
        seed=seed,
        preview_enabled=bool(preview_enabled_var.get()),
        preview_scale=preview_scale,
        preview_mode=preview_mode_var.get(),
        preview_only=bool(preview_only_var.get()),
    )


def on_closing():
    save_window_state(root)
    for process in running_processes:
        if process.poll() is None:
            process.terminate()
    root.destroy()


def sync_preview_controls():
    if not preview_enabled_var.get():
        preview_only_var.set(0)
        preview_only_checkbutton.config(state=tk.DISABLED)
        return

    preview_only_checkbutton.config(state=tk.NORMAL)


root = tk.Tk()
root.title('VOX Factory v3.2')
root.geometry(DEFAULT_WINDOW_GEOMETRY)
root.minsize(700, 380)
root.protocol('WM_DELETE_WINDOW', on_closing)

window_state = load_window_state()
root.geometry(window_state['geometry'])
if window_state['zoomed']:
    root.state('zoomed')

main_frame = tk.Frame(root, padx=14, pady=14)
main_frame.pack(fill=tk.BOTH, expand=True)
main_frame.grid_columnconfigure(0, weight=3)
main_frame.grid_columnconfigure(1, weight=2)
main_frame.grid_rowconfigure(0, weight=1)

left_panel = tk.Frame(main_frame)
left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
left_panel.grid_rowconfigure(1, weight=1)
left_panel.grid_columnconfigure(0, weight=1)

tk.Label(left_panel, text='Voxel blueprints in /vox_blueprints:', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 6))
listbox = tk.Listbox(left_panel, font=('Consolas', 10), exportselection=False)
listbox.grid(row=1, column=0, sticky='nsew')
listbox.bind('<<ListboxSelect>>', on_select)

right_panel = tk.Frame(main_frame)
right_panel.grid(row=0, column=1, sticky='nsew')
right_panel.grid_columnconfigure(0, weight=1)

frame_info = tk.LabelFrame(right_panel, text=' Blueprint Info ', padx=10, pady=8)
frame_info.grid(row=0, column=0, sticky='ew')
frame_info.grid_columnconfigure(0, weight=1)
info_name_var = tk.StringVar(value='No blueprint selected')
info_seed_var = tk.StringVar(value='Seeded variants: unavailable')
info_palette_var = tk.StringVar(value='Embedded palette: MagicaVoxel pal0 baseline')
tk.Label(frame_info, textvariable=info_name_var, anchor='w', font=('Arial', 10, 'bold')).pack(fill=tk.X)
tk.Label(frame_info, textvariable=info_seed_var, anchor='w').pack(fill=tk.X)
tk.Label(frame_info, textvariable=info_palette_var, anchor='w').pack(fill=tk.X)

frame_description = tk.Frame(frame_info)
frame_description.pack(fill=tk.X, pady=(8, 0))
frame_description.grid_columnconfigure(0, weight=1)

txt_description = tk.Text(frame_description, height=5, wrap=tk.WORD, font=('Arial', 9), relief=tk.SUNKEN, borderwidth=1)
txt_description.grid(row=0, column=0, sticky='ew')
description_scrollbar = tk.Scrollbar(frame_description, command=txt_description.yview)
description_scrollbar.grid(row=0, column=1, sticky='ns')
txt_description.config(yscrollcommand=description_scrollbar.set, state=tk.DISABLED)
set_info_description('')

frame_build = tk.LabelFrame(right_panel, text=' Build Settings ', padx=10, pady=10)
frame_build.grid(row=1, column=0, sticky='ew', pady=(10, 0))
frame_build.grid_columnconfigure(1, weight=1)
frame_build.grid_columnconfigure(3, weight=1)
frame_build.grid_columnconfigure(5, weight=1)

tk.Label(frame_build, text='Width').grid(row=0, column=0, sticky='w')
ent_w = tk.Entry(frame_build, width=7)
ent_w.grid(row=0, column=1, sticky='ew', padx=(6, 10))
tk.Label(frame_build, text='Depth').grid(row=0, column=2, sticky='w')
ent_d = tk.Entry(frame_build, width=7)
ent_d.grid(row=0, column=3, sticky='ew', padx=(6, 10))
tk.Label(frame_build, text='Height').grid(row=0, column=4, sticky='w')
ent_h = tk.Entry(frame_build, width=7)
ent_h.grid(row=0, column=5, sticky='ew', padx=(6, 0))

tk.Label(frame_build, text='Output name').grid(row=1, column=0, sticky='w', pady=(10, 0))
ent_output = tk.Entry(frame_build)
ent_output.grid(row=1, column=1, columnspan=5, sticky='ew', pady=(10, 0))

tk.Label(frame_build, text='Optional seed').grid(row=2, column=0, sticky='w', pady=(10, 0))
ent_seed = tk.Entry(frame_build)
ent_seed.grid(row=2, column=1, columnspan=5, sticky='ew', pady=(10, 0))

preview_enabled_var = tk.IntVar(value=1 if window_state.get('preview_enabled', True) else 0)
preview_enabled_checkbutton = tk.Checkbutton(frame_build, text='Save PNG preview', variable=preview_enabled_var, command=sync_preview_controls)
preview_enabled_checkbutton.grid(row=3, column=0, columnspan=2, sticky='w', pady=(10, 0))

preview_only_var = tk.IntVar(value=1 if window_state.get('preview_only', False) else 0)
preview_only_checkbutton = tk.Checkbutton(frame_build, text='Preview only (skip .vox)', variable=preview_only_var)
preview_only_checkbutton.grid(row=4, column=0, columnspan=3, sticky='w', pady=(8, 0))

preview_mode_var = tk.StringVar(value=window_state.get('preview_mode', DEFAULT_PREVIEW_MODE))
tk.Label(frame_build, text='Preview mode').grid(row=3, column=2, sticky='w', pady=(10, 0))
preview_mode_menu = tk.OptionMenu(frame_build, preview_mode_var, 'orthographic', 'isometric', 'both', 'top')
preview_mode_menu.grid(row=3, column=3, sticky='ew', padx=(6, 10), pady=(10, 0))

tk.Label(frame_build, text='Preview scale').grid(row=3, column=4, sticky='w', pady=(10, 0))
ent_preview_scale = tk.Entry(frame_build, width=7)
ent_preview_scale.grid(row=3, column=5, sticky='ew', padx=(6, 0), pady=(10, 0))
ent_preview_scale.insert(0, window_state.get('preview_scale', DEFAULT_PREVIEW_SCALE))

sync_preview_controls()

frame_tools = tk.Frame(right_panel)
frame_tools.grid(row=2, column=0, sticky='ew', pady=(10, 0))
frame_tools.grid_columnconfigure(0, weight=1)
frame_tools.grid_columnconfigure(1, weight=1)
tk.Button(frame_tools, text='Refresh', command=refresh).grid(row=0, column=0, sticky='ew', padx=(0, 5))
tk.Button(frame_tools, text='Outputs (.vox + previews)', command=open_models_folder).grid(row=0, column=1, sticky='ew', padx=(5, 0))

frame_actions = tk.Frame(right_panel)
frame_actions.grid(row=3, column=0, sticky='ew', pady=(10, 0))
frame_actions.grid_columnconfigure(0, weight=1)

btn_run = tk.Button(frame_actions, text='START BUILD', bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), height=2, command=run_selected)
btn_run.grid(row=0, column=0, sticky='ew')

refresh()
root.mainloop()
