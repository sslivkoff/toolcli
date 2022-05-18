from __future__ import annotations


def get_n_terminal_cols() -> int:
    import subprocess

    # TODO: platform independent method
    output = subprocess.check_output('tput cols', shell=True)
    return int(output)


def get_n_terminal_rows() -> int:
    import subprocess

    # TODO: platform independent method
    output = subprocess.check_output('tput lines', shell=True)
    return int(output)

