from __future__ import annotations

import importlib
import types

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': spec_command,
        'help': 'edit the definition of a given command sequence',
        'args': [
            {'name': 'command_sequence', 'nargs': '+'},
        ],
        'hidden': True,
        'extra_data': ['parse_spec'],
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
            if isinstance(reference, str):
                module = importlib.import_module(reference)
            elif isinstance(reference, types.ModuleType):
                module = reference
            else:
                raise Exception('could not determine path where command is defined')

            if hasattr(module, '__path__'):
                path = module.__path__[0]
            elif hasattr(module, '__file__') and module.__file__ is not None:
                path = module.__file__
            else:
                raise Exception('could not determine module path')
            toolcli.open_file_in_editor(path)
