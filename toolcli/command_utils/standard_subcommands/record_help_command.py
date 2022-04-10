from __future__ import annotations

import os

from toolcli.command_utils import help_utils
from toolcli.command_utils import output_utils
from toolcli import capture_utils


def get_command_spec():
    return {
        'f': record_help_command,
        'help': 'record help output to an html or svg file',
        'args': [
            {'name': 'subcommand', 'nargs': '*'},
            {'name': '--path'},
            {'name': '--overwrite', 'action': 'store_true'},
        ],
        'special': {
            'include_parse_spec': True,
        },
    }


def record_help_command(subcommand, path, overwrite, parse_spec):
    if path is None:
        if len(subcommand) == 0:
            path = 'help.html'
        else:
            path = '_'.join(subcommand) + '__help.html'

    if os.path.isfile(path) and not overwrite:
        raise Exception(
            'path already exists, use --overwrite to force overwrite'
        )

    # create console
    console = output_utils.get_rich_console(parse_spec, record=True)

    # produce output
    if len(subcommand) == 0:
        help_utils.print_root_command_help(
            parse_spec=parse_spec, console=console
        )
    else:
        help_utils.print_root_command_help(
            parse_spec=parse_spec, console=console
        )

    # save console output
    capture_utils.save_console_output(
        console=console,
        path=path,
    )

    print()
    print('recorded help to path: ' + str(path))

