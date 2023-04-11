#!/usr/bin/env python3

import logging
import os
import platform
import re
import subprocess
import sys
import textwrap
import warnings
from pathlib import Path
from shutil import copy

import click
import pyperclip
from appdirs import user_config_dir
from daemonize import Daemonize

import picker

APPLICATION_NAME = "inkscape-figure-manager"
# os-agnostic path to current user's configuration directory for this
# application
APP_USER_CONFIG_DIR = Path(user_config_dir(APPLICATION_NAME, False))
ROOT_FILE_PATH = APP_USER_CONFIG_DIR / 'roots'
TEMPLATE_FILE_PATH = APP_USER_CONFIG_DIR / 'template.svg'
# error codes:
ERROR_CODE_CREATED_FILE_ALREADY_EXISTS = 1
ERROR_CODE_EDITED_FILE_PATH_DOES_NOT_EXIST = 2

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger('inkscape-figures')


# def indent(text, indentation=0):
#     lines = text.split('\n')
#     return '\n'.join(" " * indentation + line for line in lines)


def snake_case(string):
    """
    Returns the snake case form of the passed string. Spaces and
    dashes are replaced with underscores, and the string is made lowercase.
    """
    return string.lower().replace(' ', '_').replace('-', ' ')


def markdown_include_image_text(image_alternate_text, image_path):
    """
    returns the markdown text for including an image

    first parameter is the image's alternate text
    second parameter is the image's path
    """
    return rf"![{image_alternate_text}]({image_path})"


def open_inkscape(open_file_path):
    """
    Starts the Inkscape application opening the 'open_file_path'.
    """
    with warnings.catch_warnings():
        # leaving a subprocess running after interpreter exit raises a
        # warning in Python3.7+
        warnings.simplefilter("ignore", ResourceWarning)
        subprocess.Popen(['inkscape', str(open_file_path)])


# def add_root(path):
#    path = str(path)
#    roots = get_roots()
#    if path in roots:
#        return None
#
#    roots.append(path)
#    ROOT_FILE_PATH.write_text('\n'.join(roots))
#
#
# def get_roots():
#    return [root for root in ROOT_FILE_PATH.read_text().split('\n') if root != '']


@click.group()
def cli():
    """
    Wrapper function for the CLI from the click library.
    """


# @cli.command()
# @click.option('--daemon/--no-daemon', default=True)
# def watch(daemon):
#     """
#     Watches for figures.
#     """
#     if platform.system() == 'Linux':
#         watcher_cmd = watch_daemon_inotify
#     else:
#         watcher_cmd = watch_daemon_fswatch
#
#     if daemon:
#         daemon = Daemonize(app='inkscape-figures',
#                            pid='/tmp/inkscape-figures.pid',
#                            action=watcher_cmd)
#         daemon.start()
#         log.info("Watching figures.")
#     else:
#         log.info("Watching figures.")
#         watcher_cmd()
#
#
# def maybe_recompile_figure(filepath):
#     filepath = Path(filepath)
#     # A file has changed
#     if filepath.suffix != '.svg':
#         log.debug('File has changed, but is nog an svg {}'.format(
#             filepath.suffix))
#         return
#
#     log.info('Recompiling %s', filepath)
#
#     pdf_path = filepath.parent / (filepath.stem + '.pdf')
#     name = filepath.stem
#
#     inkscape_version = subprocess.check_output(
#         ['inkscape', '--version'], universal_newlines=True)
#     log.debug(inkscape_version)
#
#     # Convert
#     # - 'Inkscape 0.92.4 (unknown)' to [0, 92, 4]
#     # - 'Inkscape 1.1-dev (3a9df5bcce, 2020-03-18)' to [1, 1]
#     # - 'Inkscape 1.0rc1' to [1, 0]
#     inkscape_version = re.findall(r'[0-9.]+', inkscape_version)[0]
#     inkscape_version_number = [int(part)
#                                for part in inkscape_version.split('.')]
#
#     # Right-pad the array with zeros (so [1, 1] becomes [1, 1, 0])
#     inkscape_version_number = inkscape_version_number + \
#         [0] * (3 - len(inkscape_version_number))
#
#     # Tuple comparison is like version comparison
#     if inkscape_version_number < [1, 0, 0]:
#         command = [
#             'inkscape',
#             '--export-area-page',
#             '--export-dpi', '300',
#             '--export-pdf', pdf_path,
#             '--export-latex', filepath
#         ]
#     else:
#         command = [
#             'inkscape', filepath,
#             '--export-area-page',
#             '--export-dpi', '300',
#             '--export-type=pdf',
#             '--export-latex',
#             '--export-filename', pdf_path
#         ]
#
#     log.debug('Running command:')
#     log.debug(textwrap.indent(' '.join(str(e) for e in command), '    '))
#
#     # Recompile the svg file
#     completed_process = subprocess.run(command)
#
#     if completed_process.returncode != 0:
#         log.error('Return code %s', completed_process.returncode)
#     else:
#         log.debug('Command succeeded')
#
#     # Copy the LaTeX code to include the file to the clipboard
#     template = latex_template(name, beautify(name))
#     pyperclip.copy(template)
#     log.debug('Copying LaTeX template:')
#     log.debug(textwrap.indent(template, '    '))
#
#
# def watch_daemon_inotify():
#     import inotify.adapters
#     from inotify.constants import IN_CLOSE_WRITE
#
#     while True:
#         roots = get_roots()
#
#         # Watch the file with contains the paths to watch
#         # When this file changes, we update the watches.
#         i = inotify.adapters.Inotify()
#         i.add_watch(str(ROOT_FILE_PATH), mask=IN_CLOSE_WRITE)
#
#         # Watch the actual figure directories
#         log.info('Watching directories: ' + ', '.join(get_roots()))
#         for root in roots:
#             try:
#                 i.add_watch(root, mask=IN_CLOSE_WRITE)
#             except Exception:
#                 log.debug('Could not add root %s', root)
#
#         for event in i.event_gen(yield_nones=False):
#             (_, type_names, path, filename) = event
#
#             # If the file containing figure roots has changes, update the
#             # watches
#             if path == str(ROOT_FILE_PATH):
#                 log.info('The roots file has been updated. Updating watches.')
#                 for root in roots:
#                     try:
#                         i.remove_watch(root)
#                         log.debug('Removed root %s', root)
#                     except Exception:
#                         log.debug('Could not remove root %s', root)
#                 # Break out of the loop, setting up new watches.
#                 break
#
#             # A file has changed
#             path = Path(path) / filename
#             maybe_recompile_figure(path)
#
#
# def watch_daemon_fswatch():
#     while True:
#         roots = get_roots()
#         log.info('Watching directories: ' + ', '.join(roots))
#         # Watch the figures directories, as weel as the config directory
#         # containing the roots file (file containing the figures to the figure
#         # directories to watch). If the latter changes, restart the watches.
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore", ResourceWarning)
#             p = subprocess.Popen(
#                 ['fswatch', *roots, str(APP_USER_CONFIG_DIR)], stdout=subprocess.PIPE,
#                 universal_newlines=True)
#
#         while True:
#             filepath = p.stdout.readline().strip()
#
#             # If the file containing figure roots has changes, update the
#             # watches
#             if filepath == str(ROOT_FILE_PATH):
#                 log.info('The roots file has been updated. Updating watches.')
#                 p.terminate()
#                 log.debug('Removed main watch %s')
#                 break
#             maybe_recompile_figure(filepath)


@cli.command()
@click.argument('alternate_text')
@click.argument(
    'figure_dir',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True)
)
def create(alternate_text, figure_dir):
    """
    Creates a figure with named using the snake-case form of the alternate
    text.

    First argument is the alternate text of the image
    Second argument is the figure directory.

    Errors: If a figure already exists with the provided name, the program will
            not do anything except return with a non-zero exit status.
    """
    alternate_text = alternate_text.strip()
    file_name = alternate_text.replace(' ', '-').lower() + '.svg'
    figure_dir = Path(figure_dir).absolute()
    if not figure_dir.exists():
        figure_dir.mkdir()
    file_path = figure_dir / file_name

    # If a file with this name already exists, append a '2'.
    if file_path.exists():
        print(f"A file with the same name already exists at '{file_path}'")
        sys.exit(ERROR_CODE_CREATED_FILE_ALREADY_EXISTS)

    copy(str(TEMPLATE_FILE_PATH), str(file_path))
    # add_root(figure_dir)
    open_inkscape(file_path)

    print(markdown_include_image_text(alternate_text, file_path.stem))


@cli.command()
@click.argument(
    'path',
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
)
def edit(path):
    """
    Edits a figure.

    PATH: The path to either a figure or a directory containing one or more
    figures. When multiple figures are within the directory, a picker will
    be used for selection. Default is the current working directory.
    """
    path = Path(path).absolute()

    # ensure path exists
    if not path.exists():
        print(f"The path does not exsist; received '{path}'.")
        sys.exit(ERROR_CODE_EDITED_FILE_PATH_DOES_NOT_EXIST)

    selected_file = None
    if path.is_file():
        selected_file = path

    elif path.is_dir():
        # Find svg files and sort them
        files = path.glob('*.svg')
        files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

        # if there is only one figure in the directory select it
        if len(files) == 1:
            selected_file = files[0]
            print(selected_file)
        # otherwise launch the picker for selection
        else:
            names = [f.stem for f in files]
            returncode, index = picker.pick(names)
            if returncode != 0:
                print("Picker returned with non-zero exit status.")
                return
            if index is ValueError:
                print("A value error occurred while choosing with the picker.")
                return
            selected_file = files[index]

        open_inkscape(selected_file)

    # Castel's code added the selected file to the "root" basically a file
    # tracking figures. IDK if I should be doing this as well.


def ensure_init():
    if not APP_USER_CONFIG_DIR.is_dir():
        APP_USER_CONFIG_DIR.mkdir()

    if not ROOT_FILE_PATH.is_file():
        ROOT_FILE_PATH.touch()

    # if template file does not exist, copy it from the template file in this
    # directory
    if not TEMPLATE_FILE_PATH.is_file():
        copy(str(Path(__file__).parent / 'template.svg'),
             str(TEMPLATE_FILE_PATH))


if __name__ == '__main__':
    ensure_init()
    cli()
