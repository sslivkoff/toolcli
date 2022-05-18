from __future__ import annotations

import rich

from toolcli import spec
from toolcli.command_utils.parsing import command_parsing


def get_command_spec() -> spec.CommandSpec:
    return {
        'f': spec_command,
        'help': 'print command spec for a given command sequence',
        'args': [
            {'name': 'command_sequence', 'nargs': '+'},
        ],
        'hidden': True,
        'extra_data': ['parse_spec'],
    }


def spec_command(
    command_sequence: list[str], parse_spec: spec.ParseSpec
) -> None:
    command_index = parse_spec.get('command_index')
    if command_index is None:
        print('no command index specified')
    else:
        reference = command_index.get(tuple(command_sequence))
        if reference is None:
            print('could not find spec for given command sequence')
        else:
            command_spec = command_parsing.resolve_command_spec(reference)
            rich.print(command_spec)
