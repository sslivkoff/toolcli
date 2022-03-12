import rich

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': spec_command,
        'help': 'print command spec for a given command sequence',
        'args': [
            {'name': 'command_sequence', 'nargs': '+'},
        ],
        'special': {
            'include_parse_spec': True,
            'hidden': True,
        },
    }


def spec_command(
    command_sequence: list[str], parse_spec: toolcli.ParseSpec
) -> None:
    command_index = parse_spec.get('command_index')
    if command_index is None:
        print('no command index specified')
    else:
        reference = command_index.get(tuple(command_sequence))
        if reference is None:
            print('could not find spec for given command sequence')
        else:
            command_spec = toolcli.resolve_command_spec(reference)
            rich.print(command_spec)

