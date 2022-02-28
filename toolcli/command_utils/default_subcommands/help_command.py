from __future__ import annotations

import toolcli
import tooltable  # type: ignore


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': help_command,
        'help': 'output help',
        'special': {
            'parse_spec': True,
        },
    }


def help_command(parse_spec: toolcli.ParseSpec) -> None:

    config = parse_spec['config']
    command_index = parse_spec['command_index']
    base_command = config.get('base_command', '<base-command>')

    print('usage: ' + base_command + ' <subcommand> [options]')
    print()
    if config.get('description') is not None:
        print(config['description'])
        print()
    print(
        'to view help about a specific subcommand run:\n    '
        + base_command
        + ' <subcommand> -h'
    )

    if command_index is not None:
        rows = []
        for command_sequence, command_spec_spec in command_index.items():
            command_spec = toolcli.resolve_command_spec(command_spec_spec)
            row = []
            row.append(' '.join(command_sequence))
            row.append(command_spec.get('help', ''))
            rows.append(row)

        print()
        print('available subcommands:')

        tooltable.print_table(
            rows=rows,
            headers=None,
            vertical_border=' ',
            cross_border=' ',
            horizontal_border=' ',
            indent='  ',
        )

