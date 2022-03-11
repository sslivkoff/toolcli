from __future__ import annotations

import os
import typing


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


# def open_json_in_editor(obj: typing.IO[str], inplace: bool = False) -> None:
#     """interactively edit nested json object"""
#     choices = [
#         'Edit in editor',
#         'Edit specific location in editor',
#         'Enter raw data',
#         'Enter raw data for location',
#         'Done',
#     ]
#     answer = input_utils.input_numbered_choice(choices=choices)

#     if answer == 'Edit in editor':
#         # dump to temporary file
#         tmp_handle, tmp_path = tempfile.mkstemp()
#         json.dump(obj, tmp_handle)

#         # edit in editor
#         editor_command = get_editor_command()
#         subprocess.call([editor_command, tmp_path], shell=False)
#         tmp_handle.close()

#     elif answer == 'Edit specific location in editor':
#         obj = edit_json_location(obj=obj, inplace=inplace)

#         return open_json_in_editor(obj, inplace=inplace)

#     elif answer == 'Enter raw data':
#         try:
#             new_raw_data = input('Enter raw data:')
#             new_obj = json.loads(new_raw_data)
#         except json.JSONDecodeError:
#             print('invalid json')
#         return edit_json(obj, inplace=inplace)

#     elif answer == 'Enter raw data for specific location':
#         pass

#     elif answer == 'Done':
#         return obj

#     else:
#         raise Exception('must be one of: ' + ', '.join(choices))


# def edit_json_location(obj, location=None, inplace=False):

#     # obtain location
#     if location is None:
#         print('separate the indices with commas')
#         answer = input('Enter location: ')
#         location = answer.split(',')
#     elif isinstance(location, str):
#         location = location.split(',')

#     # check if obj has a value for this location
#     current_value = None
#     if not location_utils.has_location(obj, location):
#         print('this location does not exist')
#         answer = input_yes_or_no(prompt='should create it?')
#         if answer:
#             pass
#         else:
#             pass
#     else:
#         current_value = location_utils.get_location(obj, location)
#         print('current value:', str(current_value))

#     # enter new value
#     new_value = input('new value:')

#     # validate new value
#     try:
#         new_value_as_json = json.loads(new_value)
#         answer = input_numbered_choice(
#             prompt='parse as json or plain str?',
#             choices=['json', 'str'],
#         )
#         if answer == 'json':
#             location.set_location(obj, location, new_value_as_json)
#         elif answer == 'str':
#             location.set_location(obj, location, new_value)
#         else:
#             raise Exception('must choose json or str')
#     except Exception:
#         location.set_location(obj, location, new_value)

