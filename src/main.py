#!/usr/bin/env python3

import logging
import os
import subprocess
import sys
import warnings
from pathlib import Path
from shutil import copy

import click
from appdirs import user_config_dir

import picker
import file_system_watcher

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


@click.group()
def cli():
    """
    Wrapper function for the CLI from the click library.
    """


@cli.command()
@click.option('-g', '--git', is_flag=True, default=False, show_default=True,
              help="Watch the git repository. Searches from WATCHED_DIR")
@click.argument('watched_dir', default=Path.cwd())
def watch(git, watched_dir):
    """
    Watches a directory and its subdirectories (recursive) for changes to
    figure files (*.svg); exports the figure (*.png) when this occurs.

    WATCHED_DIR: directory to watch
    """
    if git:
        watched_dir = file_system_watcher.find_git_root(watched_dir)

    file_system_watcher.watch(watched_dir)


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


def ensure_init():
    """
    Ensures the configuration directories and a figure template exist.
    """
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
