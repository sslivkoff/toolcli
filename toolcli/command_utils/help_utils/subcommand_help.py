from __future__ import annotations

import typing

import toolcli
from .. import parsing


def print_subcommand_usage(
    parse_spec: toolcli.ParseSpec,
    indent: typing.Optional[str] = None,
) -> None:
    """print usage for a subcommand"""

    import rich.console
    import rich.theme

    style_theme = parse_spec['config'].get('style_theme')
    if style_theme is None:
        style_theme = {}
    console = rich.console.Console(
        theme=rich.theme.Theme(style_theme, inherit=False)  # type: ignore
    )

    config = parse_spec['config']
    command_sequence = parse_spec['command_sequence']
    command_spec = parse_spec['command_spec']

    required_args = []
    for arg_spec in command_spec.get('args', []):
        name = arg_spec['name']
        if isinstance(name, str) and not name.startswith('-'):
            metavar = name.upper().replace('-', '_')
            if arg_spec.get('nargs') == '?':
                metavar = '[' + metavar + ']'
            metavar = '[metavar]' + metavar + '[metavar]'
            required_args.append(metavar)

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

    usage_str = '[option]' + config['base_command']
    if command_sequence is not None:
        usage_str += ' ' + ' '.join(command_sequence)
    usage_str += ' ' + ' '.join(required_args)
    usage_str += ' \[options][/option]'

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


def print_subcommand_help(parse_spec: toolcli.ParseSpec) -> None:
    """print help for a subcommand"""

    import rich.console
    import rich.theme

    style_theme = parse_spec['config'].get('style_theme')
    if style_theme is None:
        style_theme = {}
    console = rich.console.Console(
        theme=rich.theme.Theme(style_theme, inherit=False)  # type: ignore
    )

    command_spec = parse_spec['command_spec']

    print_subcommand_usage(parse_spec, indent='    ')

    # print description
    if 'help' in command_spec:
        print()
        console.print('[title]description:[/title]')
        indent = '    '
        command_help = command_spec['help']
        lines = [indent + line for line in command_help.split('\n')]
        command_help = '\n'.join(lines)
        console.print('[description]' + command_help + '[/description]')

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

                command_spec = parsing.resolve_command_spec(other_reference)
                description = command_spec.get('help')
                if description is None:
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
                subsubcommand = ' '.join(subsubcommand).ljust(max_length)
                console.print(
                    '    [option]'
                    + subsubcommand
                    + '[/option]    [description]'
                    + description
                    + '[/description]'
                )

