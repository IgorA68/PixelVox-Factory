import json
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from pixel_art.blueprint_utils import PIXEL_BLUEPRINTS_DIR
from pixel_art.blueprint_utils import PROJECT_ROOT
from pixel_art.blueprint_utils import discover_blueprint_files
from pixel_art.blueprint_utils import get_blueprint_metadata
from pixel_art.blueprint_utils import load_blueprint_module
from pixel_art.blueprint_utils import validate_blueprint_module


running_processes = []
current_loaded_file = None
blueprint_entries = {}
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'images')
PIXEL_GUI_STATE_PATH = os.path.join(PROJECT_ROOT, '.pixel_gui_state.json')
DEFAULT_WINDOW_GEOMETRY = '760x430'
DEFAULT_EXPORT_SCALE = '8'


def load_window_state():
    if not os.path.exists(PIXEL_GUI_STATE_PATH):
        return {'geometry': DEFAULT_WINDOW_GEOMETRY, 'zoomed': False, 'export_scale': DEFAULT_EXPORT_SCALE}

    try:
        with open(PIXEL_GUI_STATE_PATH, 'r', encoding='utf-8') as handle:
            state = json.load(handle)
    except (OSError, ValueError, TypeError):
        return {'geometry': DEFAULT_WINDOW_GEOMETRY, 'zoomed': False, 'export_scale': DEFAULT_EXPORT_SCALE}

    geometry = state.get('geometry', DEFAULT_WINDOW_GEOMETRY)
    zoomed = bool(state.get('zoomed', False))
    export_scale = str(state.get('export_scale', DEFAULT_EXPORT_SCALE))

    if not isinstance(geometry, str) or not re.fullmatch(r'\d+x\d+([+-]\d+){2}', geometry):
        geometry = DEFAULT_WINDOW_GEOMETRY

    if not re.fullmatch(r'\d+', export_scale) or int(export_scale) <= 0:
        export_scale = DEFAULT_EXPORT_SCALE

    return {'geometry': geometry, 'zoomed': zoomed, 'export_scale': export_scale}


def save_window_state(root_window):
    state = {
        'geometry': root_window.geometry(),
        'zoomed': root_window.state() == 'zoomed',
        'export_scale': ent_scale.get().strip() or DEFAULT_EXPORT_SCALE,
    }

    try:
        with open(PIXEL_GUI_STATE_PATH, 'w', encoding='utf-8') as handle:
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
        messagebox.showerror('Blueprint error', f'{os.path.basename(script_path)} does not match the pixel blueprint contract.\n\n{exc}')
        return False
    except Exception as exc:
        messagebox.showerror('Blueprint error', f'Could not load {os.path.basename(script_path)}.\n\n{type(exc).__name__}: {exc}')
        return False

    return True


def ensure_blueprints_dir():
    if os.path.isdir(PIXEL_BLUEPRINTS_DIR):
        return True

    messagebox.showerror('Project error', f'The pixel_blueprints folder was not found:\n{PIXEL_BLUEPRINTS_DIR}')
    return False


def open_images_folder():
    if not os.path.isdir(IMAGES_DIR):
        messagebox.showinfo('Output folder', f'The output folder does not exist yet. It will be created after the first successful build and will contain generated PNG pixel-art assets.\n\nPath:\n{IMAGES_DIR}')
        return

    os.startfile(IMAGES_DIR)


def launch_build(script_path, width, height, output_name, seed=None, scale=8):
    python_exe = resolve_python_executable()
    command = [
        python_exe,
        '-m', 'pixel_art.build_blueprint',
        script_path,
        '--width', str(width),
        '--height', str(height),
        '--output-name', output_name,
        '--scale', str(scale),
    ]

    if seed is not None:
        command.extend(['--seed', str(seed)])

    try:
        proc = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=PROJECT_ROOT)
        running_processes.append(proc)
    except Exception as exc:
        messagebox.showerror('Launch error', f'Could not start the build process:\n{exc}')


def launch_showcase_batch():
    python_exe = resolve_python_executable()
    command = [python_exe, '-m', 'pixel_art.build_demo_assets']

    try:
        proc = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=PROJECT_ROOT)
        running_processes.append(proc)
    except Exception as exc:
        messagebox.showerror('Launch error', f'Could not start the showcase build process:\n{exc}')


def refresh():
    global current_loaded_file
    global blueprint_entries

    listbox.delete(0, tk.END)
    blueprint_entries = {}

    if not ensure_blueprints_dir():
        current_loaded_file = None
        info_name_var.set('No pixel blueprint selected')
        set_info_description('')
        info_seed_var.set('Seeded variants: unavailable')
        info_palette_var.set('Palette overrides: unavailable')
        return

    blueprints = discover_blueprint_files(PIXEL_BLUEPRINTS_DIR)
    for item in blueprints:
        script_path = os.path.join(PIXEL_BLUEPRINTS_DIR, item)
        display_name = os.path.splitext(item)[0]
        description = ''
        try:
            module = load_blueprint_module(script_path)
            metadata = get_blueprint_metadata(module, fallback_name=display_name)
            display_name = metadata['display_name']
            description = metadata['description']
        except Exception:
            metadata = None

        blueprint_entries[item] = {'path': script_path, 'display_name': display_name, 'description': description, 'metadata': metadata}
        listbox.insert(tk.END, f'{display_name}  [{item}]')

    if not blueprints:
        messagebox.showinfo('No blueprints found', f'The pixel_blueprints folder does not contain any .py files.\n\nPath:\n{PIXEL_BLUEPRINTS_DIR}')


def on_select(evt):
    global current_loaded_file
    selection = evt.widget.curselection()
    if not selection:
        return

    selected_index = selection[0]
    selected_file = discover_blueprint_files(PIXEL_BLUEPRINTS_DIR)[selected_index]
    if selected_file == current_loaded_file:
        return

    current_loaded_file = selected_file
    entry = blueprint_entries.get(selected_file, {})
    metadata = entry.get('metadata') or {}
    script_name = os.path.splitext(selected_file)[0]

    recommended_w = metadata.get('recommended_width', 16)
    recommended_h = metadata.get('recommended_height', 16)
    info_name_var.set(entry.get('display_name', script_name))
    set_info_description(entry.get('description', ''))
    info_seed_var.set('Seeded variants: supported' if metadata.get('supports_seed') else 'Seeded variants: not supported')
    info_palette_var.set('Palette overrides: custom' if metadata.get('has_custom_palette') else 'Palette overrides: baseline palette only')

    ent_w.delete(0, tk.END)
    ent_w.insert(0, str(recommended_w))
    ent_h.delete(0, tk.END)
    ent_h.insert(0, str(recommended_h))
    ent_seed.delete(0, tk.END)
    ent_output.delete(0, tk.END)
    ent_output.insert(0, script_name)


def run_selected():
    if not ensure_blueprints_dir():
        return

    selection = listbox.curselection()
    blueprint_files = discover_blueprint_files(PIXEL_BLUEPRINTS_DIR)
    script_name = blueprint_files[selection[0]] if selection else current_loaded_file
    if not script_name:
        messagebox.showwarning('No selection', 'Select a pixel blueprint first.')
        return

    blueprint_name = os.path.splitext(script_name)[0]
    script_path = os.path.join(PIXEL_BLUEPRINTS_DIR, script_name)
    output_name = sanitize_output_name(ent_output.get(), blueprint_name)

    if not validate_blueprint(script_path):
        return

    try:
        width = parse_positive_dimension(ent_w.get(), 'Width')
        height = parse_positive_dimension(ent_h.get(), 'Height')
        seed = parse_optional_seed(ent_seed.get())
        scale = parse_positive_dimension(ent_scale.get(), 'Scale')
    except ValueError as exc:
        messagebox.showwarning('Invalid settings', str(exc))
        return

    if seed is not None and output_name == blueprint_name:
        output_name = f'{blueprint_name}_seed_{seed}'

    launch_build(script_path, width, height, output_name, seed=seed, scale=scale)


def on_closing():
    save_window_state(root)
    for process in running_processes:
        if process.poll() is None:
            process.terminate()
    root.destroy()


root = tk.Tk()
root.title('Pixel Factory v1.0')
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

tk.Label(left_panel, text='Pixel blueprints in /pixel_blueprints:', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 6))
listbox = tk.Listbox(left_panel, font=('Consolas', 10), exportselection=False)
listbox.grid(row=1, column=0, sticky='nsew')
listbox.bind('<<ListboxSelect>>', on_select)
listbox.bind('<Double-Button-1>', lambda _event: run_selected())

right_panel = tk.Frame(main_frame)
right_panel.grid(row=0, column=1, sticky='nsew')
right_panel.grid_columnconfigure(0, weight=1)

frame_info = tk.LabelFrame(right_panel, text=' Pixel Blueprint Info ', padx=10, pady=8)
frame_info.grid(row=0, column=0, sticky='ew')
frame_info.grid_columnconfigure(0, weight=1)
info_name_var = tk.StringVar(value='No pixel blueprint selected')
info_seed_var = tk.StringVar(value='Seeded variants: unavailable')
info_palette_var = tk.StringVar(value='Palette overrides: baseline palette only')
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

tk.Label(frame_build, text='Width').grid(row=0, column=0, sticky='w')
ent_w = tk.Entry(frame_build, width=7)
ent_w.grid(row=0, column=1, sticky='ew', padx=(6, 10))
tk.Label(frame_build, text='Height').grid(row=0, column=2, sticky='w')
ent_h = tk.Entry(frame_build, width=7)
ent_h.grid(row=0, column=3, sticky='ew', padx=(6, 0))

tk.Label(frame_build, text='Output name').grid(row=1, column=0, sticky='w', pady=(10, 0))
ent_output = tk.Entry(frame_build)
ent_output.grid(row=1, column=1, columnspan=3, sticky='ew', pady=(10, 0))

tk.Label(frame_build, text='Optional seed').grid(row=2, column=0, sticky='w', pady=(10, 0))
ent_seed = tk.Entry(frame_build)
ent_seed.grid(row=2, column=1, columnspan=3, sticky='ew', pady=(10, 0))

tk.Label(frame_build, text='Export scale').grid(row=3, column=0, sticky='w', pady=(10, 0))
ent_scale = tk.Entry(frame_build)
ent_scale.grid(row=3, column=1, columnspan=3, sticky='ew', pady=(10, 0))
ent_scale.insert(0, window_state.get('export_scale', DEFAULT_EXPORT_SCALE))

frame_tools = tk.Frame(right_panel)
frame_tools.grid(row=2, column=0, sticky='ew', pady=(10, 0))
frame_tools.grid_columnconfigure(0, weight=1)
frame_tools.grid_columnconfigure(1, weight=1)
frame_tools.grid_columnconfigure(2, weight=1)
tk.Button(frame_tools, text='Refresh', command=refresh).grid(row=0, column=0, sticky='ew', padx=(0, 5))
tk.Button(frame_tools, text='Outputs (PNG)', command=open_images_folder).grid(row=0, column=1, sticky='ew', padx=5)
tk.Button(frame_tools, text='Build Showcase Set', command=launch_showcase_batch).grid(row=0, column=2, sticky='ew', padx=(5, 0))

frame_actions = tk.Frame(right_panel)
frame_actions.grid(row=3, column=0, sticky='ew', pady=(10, 0))
frame_actions.grid_columnconfigure(0, weight=1)

btn_run = tk.Button(frame_actions, text='Build Selected PNG', bg='#2E8B57', fg='white', font=('Arial', 11, 'bold'), height=2, command=run_selected)
btn_run.grid(row=0, column=0, sticky='ew')

refresh()
root.mainloop()