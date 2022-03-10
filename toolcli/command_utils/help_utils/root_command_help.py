import tooltable  # type: ignore

import toolcli


def print_root_command_help(parse_spec):

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
            subcommand_help = command_spec.get('help', '')
            subcommand_help = subcommand_help.split('\n')[0]
            row.append(subcommand_help)
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

