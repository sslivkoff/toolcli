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
    category=None,
    record_all=False,
    include_hidden=False,
):

    if record_all:
        record_all_help_commands(
            path=path,
            parse_spec=parse_spec,
            overwrite=overwrite,
            include_hidden=include_hidden,
        )
    else:
        record_single_help_command(
            subcommand=subcommand,
            path=path,
            overwrite=overwrite,
            parse_spec=parse_spec,
            category=category,
        )


def record_single_help_command(
    subcommand,
    path,
    overwrite,
    parse_spec,
    category=None,
):

    # compute path
    if path is not None and '.' not in os.path.basename(path):
        path = get_default_subcommand_path(subcommand, directory=path)
    elif path is None:
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
            only_category=category,
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
    parent = os.path.dirname(path)
    if len(parent) > 0:
        os.makedirs(parent, exist_ok=True)
    capture_utils.save_console_output(
        console=console,
        path=path,
        code_format='minimal',
    )

    print()
    print('recorded help to path: ' + str(path))


def get_default_subcommand_path(subcommand, directory=None):

    # build filename
    if len(subcommand) == 0:
        filename = 'root__help.html'
    else:
        filename = '_'.join(subcommand) + '__help.html'

    # build full path
    if directory is not None:
        path = os.path.join(directory, filename)
    else:
        path = filename

    return path


def record_all_help_commands(path, parse_spec, overwrite, include_hidden):

    if path is None:
        path = '.'
    if path is not None and not os.path.isdir(path):
        raise Exception('must specify an existing dir when recording all')

    # determine whether using categories
    config = parse_spec['config']
    help_subcommand_categories = config.get('help_subcommand_categories')
    using_categories = help_subcommand_categories is not None
    if using_categories:
        is_capital = next(iter(help_subcommand_categories.values())).isupper()
        if is_capital:
            other = 'Other'
        else:
            other = 'other'

    # record help of root command
    record_single_help_command(
        subcommand=(),
        overwrite=overwrite,
        parse_spec=parse_spec,
        path=None,
    )

    # record help of each subcommand
    for command_sequence, command_spec_ref in parse_spec['command_index'].items():

        if command_sequence == ():
            continue

        # skip hidden commands
        if not include_hidden:
            command_spec = parsing.resolve_command_spec(command_spec_ref)
            if command_spec.get('special', {}).get('hidden'):
                continue

        # determine path
        if using_categories:
            category = help_subcommand_categories.get(command_sequence, other)
            subcommand_path = os.path.join(path, 'subcommands', category)
        else:
            subcommand_path = os.path.join(path, 'subcommands')

        # record command
        record_single_help_command(
            subcommand=command_sequence,
            overwrite=overwrite,
            parse_spec=parse_spec,
            path=subcommand_path,
        )

    # record help of each subcommand category
    if using_categories:

        # gather all categories
        categories = []
        for command_sequence in parse_spec['command_index'].keys():
            category = help_subcommand_categories.get(command_sequence, other)
            if category not in categories:
                categories.append(category)

        # record help of each category
        for category in categories:
            record_single_help_command(
                subcommand=(),
                overwrite=overwrite,
                parse_spec=parse_spec,
                category=category,
                path=os.path.join(path, 'categories', category + '__help.html'),
            )

