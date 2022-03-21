import importlib

import toolcli
from toolcli.command_utils import parsing


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': annotate_command,
        'help': 'create annotated function signature of command spec',
        'args': [
            {'name': 'target', 'help': 'module path of command spec'},
        ],
        'special': {'include_parse_spec': True},
    }


def annotate_command(target: str, parse_spec: toolcli.ParseSpec) -> None:

    module = importlib.import_module(target)
    command_spec = module.get_command_spec()
    annotated = dev_utils.annotate_command_spec(command_spec)
    print(annotated)


