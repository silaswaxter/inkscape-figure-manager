# About

Provide an "api" for managing Inkscape figures. Built for Neovim integration.

Create, edit, and watch figures. Auto-exports figures when saved. This applies
to figures in directories specified with `create` (implicit), `edit`
(implicit), and `watch` (explicit) for the current session. When the watcher
background process (daemon) is stopped, the list of watched directories is lost;
therefore, one should edit their figures using the manager to ensure figures are
always being watched.

This project was forked from the deceased, Gille Castel's, project. He wrote a
[blog post](https://castel.dev/post/lecture-notes-2/) explaining his workflow which
should be mostly applicable. The following changes have been made:

- rework the watcher
- use markdown instead of LaTex.

## Requirements

- Python >= 3.7
- Supported OS:
  - Linux
  - Mac
    - untested (supported at fork from Castel's project)
- Picker:
  - [rofi](https://github.com/davatorium/rofi) for Linux
  - [choose](https://github.com/chipsenkbeil/choose) for MacOS
