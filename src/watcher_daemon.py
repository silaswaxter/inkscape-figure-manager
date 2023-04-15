import time
from multiprocessing.connection import Client, Listener
from pathlib import Path

from daemon import Daemon
from watcher import Watcher


class WatcherDaemon(Daemon):
    _CONN_ADDRESS = ('localhost', 6969)
    _CONN_KEY = b'qRFax5Kz@FDCY&Z&'  # we care about security here XD

    @staticmethod
    def ensure_watch(path):
        """
        Intended to be called by clients. Sends a message to the running
        watcher daemon instructing it to ensure its watching `path`
        """
        # this shitty timeout will be good enough
        timeout_length = 4
        timeout_start = time.time()
        while (timeout_start + timeout_length) >= time.time():
            try:
                with Client(WatcherDaemon._CONN_ADDRESS,
                            authkey=WatcherDaemon._CONN_KEY) as conn:
                    conn.send(path)
                    break
            except Exception as e:
                pass

    def work(self):
        """
        `main` function for the daemon.

        The daemon acts as a server watching a set of directories and
        listening for new clients and their messages (which are directories)
        """

        watcher = Watcher()
        watched_dirs = []

        print("daemon launched")

        while True:
            add_new_dir = True
            with Listener(WatcherDaemon._CONN_ADDRESS,
                          authkey=WatcherDaemon._CONN_KEY) as listener:
                with listener.accept() as conn:
                    new_dir = Path(conn.recv())
                    if new_dir not in watched_dirs:
                        for watched_dir in watched_dirs.copy():
                            # TODO: consider using PurePath.is_relative_to()
                            # check if new_dir will be watching existing dir
                            for parent in watched_dir.parents:
                                if new_dir == parent:
                                    watcher.unwatch(watched_dir)
                                    watched_dirs.remove(watched_dir)

                            # check if existing dir already watches new_dir
                            for parent in new_dir.parents:
                                if watched_dir == parent:
                                    add_new_dir = False

                        if add_new_dir:
                            watcher.watch(new_dir)
                            watched_dirs.append(new_dir)
