from __future__ import annotations

import toolcli
from toolcli.command_utils import dev_utils
from toolcli.command_utils import parsing


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': annotate_command,
        'help': 'create annotated function signature of command spec',
        'args': [
            {
                'name': 'command',
                'help': 'command sequence of command',
                'nargs': '+',
            },
        ],
        'hidden': True,
        'extra_data': ['parse_spec'],
    }


def annotate_command(
    command: list[str],
    parse_spec: toolcli.ParseSpec,
) -> None:
    command_sequence = tuple(command)
    command_index = parse_spec.get('command_index')
    if command_index is None:
        raise Exception('command_index not specified')
    else:
        comamnd_spec_ref = command_index[command_sequence]
        command_spec = parsing.resolve_command_spec(comamnd_spec_ref)
        annotated = dev_utils.annotate_command_spec(command_spec)
        print(annotated)
