from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': cli_index_command,
        'help': 'print command_index of possible subcommands',
        'hidden': True,
        'extra_data': ['parse_spec'],
    }


def cli_index_command(parse_spec: toolcli.ParseSpec) -> None:
    command_index = parse_spec.get('command_index')
    if command_index is None:
        print('no command index specified')
    elif len(command_index) == 0:
        print('command index is empty')
    else:
        command_sequences = list(
            ' '.join(item) for item in command_index.keys()
        )
        longest = max(len(item) for item in command_sequences)
        print('command index:')
        for command_sequence, reference in zip(
            command_sequences, command_index.values()
        ):
            if command_sequence == '':
                continue
            print(
                '    '
                + command_sequence.ljust(longest)
                + '    '
                + str(reference)
            )
