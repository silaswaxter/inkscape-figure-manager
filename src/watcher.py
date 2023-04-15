"""
My shitty interface for the file system watcher. Its used to auto export the
figure when saved.

Encapsulate a 3rd party library for OS-agnostic file watching with
inkscape-figure-manager business logic
"""

import logging
import os
import pathlib
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer as WatchDogObserver

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger('inkscape-figures')

EXPORT_EXTENSTION_NO_DOT = "png"


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
        Watcher.export_figure(event.src_path, EXPORT_EXTENSTION_NO_DOT)


class Watcher:

    def __init__(self):
        self.watched = {}
        self.observer = WatchDogObserver()
        self.observer.start()

    @staticmethod
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

    @staticmethod
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
            msg = f"The inkscape export subprocess exited with non-zero " \
                  f"return code: {completed_process.returncode}"
            sys.stderr.write(msg)

    def watch(self, watch_dir):
        """
        Watches file system for figures (*.svg files) being written.
        Auto-exports when written.
        """
        handler = FigureFileSystemEventHandler()
        observed_watch = self.observer.schedule(handler, watch_dir,
                                                recursive=True)
        self.watched[watch_dir] = observed_watch

    def unwatch(self, unwatch_dir):
        """
        Stops watching file system for figures.
        """
        observed_watch = self.watched[unwatch_dir]
        self.observer.unschedule(observed_watch)
