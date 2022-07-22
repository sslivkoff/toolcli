from __future__ import annotations


def get_n_terminal_cols(*, default: int | None = 80) -> int:
    import subprocess

    # TODO: platform independent method
    try:
        output = subprocess.check_output('tput cols', shell=True)
        return int(output)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e


def get_n_terminal_rows(*, default: int | None = 80) -> int:
    import subprocess

    # TODO: platform independent method
    try:
        output = subprocess.check_output('tput lines', shell=True)
        return int(output)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e
