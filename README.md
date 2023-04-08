# Inkscape Figure Manager

A script to manage Inkscape figures which provide a simple "api" to neovim
allowing custom, faster figure management. Supported features include:

- creating figures
- editing existing figures
  - using a picker (eg [rofi](https://github.com/davatorium/rofi)) to select a
    figure when a directory with multiple figures is passed.
- auto-export figure on  *.svg' save

A script I use to manage figures for my LaTeX documents.
More information in this [blog post](https://castel.dev/post/lecture-notes-2/).

## Requirements

- Python >= 3.7
- Supported OS:
  - Linux
  - Mac
- Picker:
  - [rofi](https://github.com/davatorium/rofi) for Linux
  - [choose](https://github.com/chipsenkbeil/choose) for MacOS
