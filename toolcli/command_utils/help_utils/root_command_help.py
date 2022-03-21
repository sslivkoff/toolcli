from __future__ import annotations

import types
import typing

import toolcli


def print_root_command_help(parse_spec: toolcli.ParseSpec) -> None:
    """print help message for a root command"""

    import rich.console
    import rich.theme

    style_theme = parse_spec['config'].get('style_theme')
    if style_theme is None:
        style_theme = {}
    console = rich.console.Console(
        theme=rich.theme.Theme(style_theme, inherit=False)  # type: ignore
    )

    config = parse_spec['config']
    command_index = parse_spec['command_index']
    base_command = config.get('base_command', '<base-command>')

    console.print(
        '[title]usage:[/title]\n    '
        + '[option]'
        + base_command
        + ' <subcommand> \[options][/option]'
    )
    print()
    console.print('[title]description:[/title]')
    if config.get('description') is not None:
        lines = ['    ' + line for line in config['description'].split('\n')]
        console.print('[description]' + '\n'.join(lines) + '[/description]')
        print()
    console.print(
        '    [description]to view help about a specific subcommand run:\n'
        + '        [option]'
        + base_command
        + ' <subcommand> -h[/option][/description]'
    )

    if command_index is not None:
        subcommands = []
        helps = []
        for command_sequence, command_spec_spec in command_index.items():
            if len(command_sequence) == 0:
                continue
            try:
                command_spec = toolcli.resolve_command_spec(command_spec_spec)
            except Exception:
                command_spec = {}
            if command_spec.get('special', {}).get('hidden'):
                continue
            subcommands.append(' '.join(command_sequence))
            subcommand_help = command_spec.get('help', '')
            if isinstance(subcommand_help, str):
                help_str = subcommand_help
            elif isinstance(subcommand_help, types.FunctionType):
                help_str = subcommand_help(parse_spec=parse_spec)
            else:
                help_str = ''
            help_str = help_str.split('\n')[0]
            helps.append(help_str)

        print()
        console.print('[title]available subcommands:[/title]')

        max_len_subcommand = max(len(subcommand) for subcommand in subcommands)
        for sc in range(len(subcommands)):
            console.print(
                '    [option]'
                + subcommands[sc].ljust(max_len_subcommand)
                + '[/option]    [description]'
                + helps[sc]
                + '[/description]'
            )

