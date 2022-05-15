from __future__ import annotations

import rich

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': config_command,
        'help': 'print cli config',
        'hidden': True,
        'extra_data': ['parse_spec'],
    }


def config_command(parse_spec: toolcli.ParseSpec) -> None:
    config = parse_spec['config']
    rich.print(config)
