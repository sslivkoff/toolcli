from __future__ import annotations

import os

from toolcli.command_utils import help_utils
from toolcli.command_utils import output_utils
from toolcli.command_utils import parsing
from toolcli import capture_utils


def get_command_spec():
    return {
        'f': record_help_command,
        'help': 'record help output to an html or svg file',
        'args': [
            {
                'name': 'subcommand',
                'nargs': '*',
                'help': 'subcommand to record help of',
            },
            {
                'name': '--path',
                'help': 'output path to html or svg file',
            },
            {
                'name': '--overwrite',
                'help': 'whether to overwrite files if they already exist',
                'action': 'store_true',
            },
            {
                'name': '--all',
                'help': 'record help for all subcommands',
                'dest': 'record_all',
                'action': 'store_true',
            },
            {
                'name': '--include-hidden',
                'help': 'if using --all, include hidden subcommands',
                'action': 'store_true',
            },
        ],
        'special': {
            'include_parse_spec': True,
        },
    }


def record_help_command(
    subcommand,
    path,
    overwrite,
    parse_spec,
    record_all=False,
    include_hidden=False,
):

    if record_all:
        record_all_help_commands(
            path, parse_spec, overwrite, include_hidden=include_hidden
        )
        return

    if path is None:
        path = get_default_subcommand_path(subcommand)
    if os.path.isfile(path) and not overwrite:
        raise Exception(
            'path already exists, use --overwrite to force overwrite'
        )

    # create console
    console = output_utils.get_rich_console(parse_spec, record=True)

    # produce output
    if len(subcommand) == 0:
        help_utils.print_root_command_help(
            parse_spec=parse_spec,
            console=console,
            include_links=True,
        )
    else:
        new_parse_spec = parsing.create_parse_spec(
            raw_command=None,
            command_index=parse_spec['command_index'],
            command_sequence=tuple(subcommand),
            command_spec=None,
            config=parse_spec['config'],
        )
        help_utils.print_subcommand_help(
            parse_spec=new_parse_spec,
            console=console,
            include_links=False,
        )

    # save console output
    capture_utils.save_console_output(
        console=console,
        path=path,
        code_format='minimal',
    )

    print()
    print('recorded help to path: ' + str(path))


def get_default_subcommand_path(subcommand):
    if len(subcommand) == 0:
        return 'help.html'
    else:
        return '_'.join(subcommand) + '__help.html'


def record_all_help_commands(path, parse_spec, overwrite, include_hidden):

    if path is not None:
        raise NotImplementedError('cannot specify path when recording all')
    # if path is not None and not os.path.isdir(path):
    #     raise Exception('must specify an existing dir when recording all')

    for subcommand, command_spec_ref in parse_spec['command_index'].items():
        if not include_hidden:
            command_spec = parsing.resolve_command_spec(command_spec_ref)
            if command_spec.get('special', {}).get('hidden'):
                continue

        record_help_command(
            subcommand=subcommand,
            overwrite=overwrite,
            parse_spec=parse_spec,
            path=None,
        )

