from __future__ import annotations

import typing
import types

import toolcli
from .. import parsing
from .. import output_utils


def print_subcommand_usage(
    parse_spec: toolcli.ParseSpec,
    indent: typing.Optional[str] = None,
) -> None:
    """print usage for a subcommand"""

    console = output_utils.get_rich_console(parse_spec)

    config = parse_spec['config']
    command_sequence = parse_spec['command_sequence']
    command_spec = parse_spec['command_spec']

    required_args = []
    n_explicit_args = 0
    n_non_hidden_args = 0
    for arg_spec in command_spec.get('args', []):
        name = arg_spec['name']
        if isinstance(name, str) and not name.startswith('-'):
            metavar = name.upper().replace('-', '_')
            if arg_spec.get('nargs') == '?':
                metavar = '[' + metavar + ']'
            metavar = '[metavar]' + metavar + '[metavar]'
            required_args.append(metavar)
            n_explicit_args += 1

        elif arg_spec.get('required'):
            if isinstance(name, str):
                flag = name
            else:
                for subname in name:
                    if subname.startswith('--'):
                        flag = subname
                        break
                else:
                    flag = name[0]
            required_args.append(flag + ' ' + get_arg_metavar(arg_spec))
            n_explicit_args += 1

        if not arg_spec.get('internal', False):
            n_non_hidden_args += 1

    usage_str = '[option]' + config['base_command']
    if command_sequence is not None:
        usage_str += ' ' + ' '.join(command_sequence)
    usage_str += ' ' + ' '.join(required_args)
    if n_explicit_args < n_non_hidden_args:
        usage_str += ' \[options]'
    usage_str += '[/option]'

    if indent:
        sep = '\n' + indent
    else:
        sep = ' '
    console.print('[title]usage:[/title]' + sep + usage_str)


def get_arg_metavar(arg_spec: toolcli.ArgSpec) -> str:
    metavar = arg_spec.get('metavar')
    if metavar is None:
        metavar = parsing.get_arg_name(arg_spec).upper()

    metavar = metavar.replace('-', '_')

    return metavar


def print_cd_dirs(*, config=None, console=None, parse_spec=None, indent=None):
    if indent is None:
        indent = ''

    if config is None:
        if parse_spec is None:
            raise Exception('must specify config or parse_spec')
        config = parse_spec.get('config')
    if console is None:
        if parse_spec is None:
            raise Exception('must specify console or parse_spec')
        console = output_utils.get_rich_console(parse_spec)

    console.print(
        indent + '[description]available directories for cd:[/description]'
    )
    for key, value in config.get('cd_dir_help', {}).items():
        console.print(
            indent + '[title]-[/title]',
            '[option]' + key + '[/option][title]:[/title]',
            '[description]' + value + '[/description]',
        )


def print_subcommand_help(parse_spec: toolcli.ParseSpec) -> None:
    """print help for a subcommand"""

    console = output_utils.get_rich_console(parse_spec)

    command_spec = parse_spec['command_spec']
    config = parse_spec.get('config')

    print_subcommand_usage(parse_spec, indent='    ')

    # print description
    if 'help' in command_spec:
        print()
        console.print('[title]description:[/title]')
        indent = '    '
        command_help = command_spec['help']
        if isinstance(command_help, str):
            help_str = command_help
        elif isinstance(command_help, types.FunctionType):
            help_str = command_help(parse_spec=parse_spec)
        else:
            help_str = ''
        lines = [indent + line for line in help_str.split('\n')]
        help_str = '\n'.join(lines)
        console.print('[description]' + help_str + '[/description]')
    if command_spec.get('special', {}).get('cd'):
        print()
        print_cd_dirs(config=config, console=console, indent='    ')

    # print arg info
    arg_names: list[str] = []
    arg_helps: list[str] = []
    for arg_spec in command_spec.get('args', []):

        # skip internal args
        if arg_spec.get('internal'):
            continue

        # arg name
        name = arg_spec['name']
        if not isinstance(name, str):
            name = ', '.join(name)
        if isinstance(name, str) and not name.startswith('-'):
            name = name.upper().replace('-', '_')
        if name.startswith('-') and arg_spec.get('action') is None:
            name += ' ' + get_arg_metavar(arg_spec)
        name = '[option]' + name + '[/option]'
        arg_names.append(name)

        # arg help
        arg_help = arg_spec.get('help')
        if arg_help is None:
            arg_help = ''
        arg_help = '[description]' + arg_help + '[/description]'
        arg_helps.append(arg_help)

    if len(arg_names) > 0:
        max_name_len = max(len(name) for name in arg_names)
        arg_names = [name.ljust(max_name_len) for name in arg_names]
        print()
        console.print('[title]arguments:[/title]')
        for a in range(len(arg_names)):
            console.print('    ' + arg_names[a] + '    ' + arg_helps[a])

    command_sequence = parse_spec['command_sequence']
    command_index = parse_spec['command_index']
    config = parse_spec['config']
    base_command = config.get('base_command')
    if base_command is None:
        base_command = '<base_command>'
    if command_sequence is not None and command_index is not None:
        subsubcommands = []
        descriptions = []
        for other_sequence, other_reference in command_index.items():
            if other_sequence == command_sequence:
                continue
            if other_sequence[: len(command_sequence)] == command_sequence:
                subsubcommands.append(other_sequence[len(command_sequence) :])

                try:
                    command_spec = parsing.resolve_command_spec(other_reference)
                except Exception:
                    command_spec = {}

                command_spec_help = command_spec.get('help')
                if isinstance(command_spec_help, str):
                    description = command_spec_help
                elif isinstance(command_spec_help, types.FunctionType):
                    description = command_spec_help(parse_spec)
                else:
                    description = ''
                descriptions.append(description)
        if len(subsubcommands) > 0:
            print()
            print()
            console.print('[title]usage of subcommands:[/title]')
            console.print(
                '    [option]'
                + base_command
                + ' '
                + ' '.join(command_sequence)
                + '[/option] [description]can also be used to invoke subcommands[/description]'
            )
            print()
            console.print(
                '    [description]to view help about a specific subcommand, run:[/description]'
            )
            console.print(
                '        [option]'
                + base_command
                + ' '
                + ' '.join(command_sequence)
                + ' <subcommand> -h[/option]'
            )
            print()
            max_length = max(
                len(' '.join(subsubcommand)) for subsubcommand in subsubcommands
            )
            console.print('[title]available subcommands:[/title]')
            for subsubcommand, description in zip(subsubcommands, descriptions):
                subsubcommand_str: str = ' '.join(subsubcommand).ljust(max_length)
                console.print(
                    '    [option]'
                    + subsubcommand_str
                    + '[/option]    [description]'
                    + description
                    + '[/description]'
                )

