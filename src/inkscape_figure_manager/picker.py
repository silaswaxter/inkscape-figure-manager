"""
Call a command line fuzzy matcher to select a figure to edit.

Current supported matchers are:

* rofi for Linux platforms
* choose (https://github.com/chipsenkbeil/choose) on MacOS
"""
import platform
import subprocess

SYSTEM_NAME = platform.system()


def get_picker_cmd(picker_args=None, fuzzy=True):
    """
    Determine and return the picker command to use
    """

    if SYSTEM_NAME == "Linux":
        args = ['rofi', '-sort', '-no-levenshtein-sort']
        if fuzzy:
            args += ['-matching', 'fuzzy']
        args += ['-dmenu', '-p', "Select Figure", '-format', 's', '-i',
                 '-lines', '5']
    elif SYSTEM_NAME == "Darwin":
        args = ["choose"]
    else:
        raise ValueError(f"No supported picker for {SYSTEM_NAME}")

    if picker_args is not None:
        args += picker_args

    return [str(arg) for arg in args]


def pick(options, picker_args=None, fuzzy=True):
    optionstr = '\n'.join(option.replace('\n', ' ') for option in options)
    result = subprocess.run(
        get_picker_cmd(picker_args=picker_args, fuzzy=fuzzy),
        input=optionstr,
        stdout=subprocess.PIPE,
        check=False,
        universal_newlines=True
    )
    returncode = result.returncode
    selected = result.stdout.strip()

    try:
        index = [opt.strip() for opt in options].index(selected)
    except ValueError:
        index = ValueError

    return returncode, index
