from __future__ import annotations

import os
import typing


def open_url_in_browser(url: str) -> None:
    import subprocess

    opener = get_opener_command()

    if not url.startswith('http'):
        if '://' in url:
            raise Exception('unknown protocol for url: ' + str(url))
        url = 'https://' + url

    subprocess.call([opener, url])


def get_opener_command() -> str:
    import subprocess

    for opener in ['xdg-open', 'open']:
        try:
            subprocess.check_output(['which', opener])
            return opener
        except subprocess.CalledProcessError:
            pass
    else:
        raise Exception('could not detect program for opening browser urls')


def get_editor_command(stdin_if_unset: bool = True) -> str:
    editor = os.environ.get('EDITOR')
    if editor is None:
        if stdin_if_unset:
            editor = input('Which editor to use? ')
        else:
            raise Exception('EDITOR environment variable unset')
    return editor


def open_file_in_editor(path: str) -> None:
    import subprocess

    editor_cmd = get_editor_command()
    if isinstance(path, str):
        cmd = [editor_cmd, path]
    else:
        cmd = [editor_cmd] + list(path)
    subprocess.call(cmd)


def open_tempfile_in_editor(initial_text: typing.Optional[str] = None) -> str:
    import tempfile

    if initial_text is None:
        initial_text = ''

    fd, path = tempfile.mkstemp()
    with open(path, 'w') as file:
        file.write(initial_text)

    open_file_in_editor(path=path)

    return path

