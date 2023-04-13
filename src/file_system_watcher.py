"""
My shitty interface for the file system watcher. Its used to auto export the
figure when saved.

Encapsulate a 3rd party library for OS-agnostic file watching with
inkscape-figure-manager business logic
"""

import logging
import os
# from pathlib import Path
import pathlib
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer as WatchDogObserver

from error_print import error_print

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger('inkscape-figures')


class FigureFileSystemEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """
        Method is scheduled with watchdog observer and will be called whenever
        a node within the observed directories is modified. If the modified
        node is a figure, export it as a `.png`.

        NOTE: Inkscape will actually fire this method twice on save. I think it
              has to do with it updating the actual file with the "buffer".
        """
        if event.is_directory:
            return
        if pathlib.Path(event.src_path).suffix != ".svg":
            return

        log.info("figure at %s modified" % (event.src_path))
        export_figure(event.src_path, "png")


def watch(directory_to_watch):
    """
    Watches file system for figures (*.svg files) being written. Auto-exports
    when written.
    """
    observer = WatchDogObserver()
    handler = FigureFileSystemEventHandler()
    observer.schedule(handler, directory_to_watch, recursive=True)
    observer.start()
    while True:
        time.sleep(1)


def export_figure(figure_path, export_extension):
    """
    Exports the figure at figure_path (*.svg) using the export_extension
    (string). The exported file will have the same name and location.
    """
    command = [
        'inkscape',
        figure_path,
        '--export-area-page',
        '--export-dpi', '300',
        f'--export-type={export_extension}',
    ]
    completed_process = subprocess.run(command, check=False)

    if completed_process.returncode != 0:
        error_print(f"The inkscape export subprocess exited with non-zero "
                    f"return code: {completed_process.returncode}")


def find_git_root(path):
    """
    Finds root of "project" which is the directory containing the '.git/'
    from path passed. If the directory does not contain a git repository,
    returns None
    """
    # ensure path is Pathlib pure path
    path = pathlib.Path(path).absolute()

    # search for git repository in parent directories
    for dir in path.parents:
        for thing in dir.iterdir():
            if thing.match('*.git'):
                if thing.is_dir():
                    return dir

    return None
