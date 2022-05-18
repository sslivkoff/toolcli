from __future__ import annotations

from toolcli import spec


def get_command_spec() -> spec.CommandSpec:
    return {
        'f': version_command,
        'help': 'print cli version',
        'args': [
            {'name': ['-V', '--version'], 'action': 'store_true'},
        ],
        'extra_data': ['parse_spec'],
    }


def version_command(parse_spec: spec.ParseSpec, version: bool) -> None:
    config_version = parse_spec['config'].get('version')
    if config_version is None:
        raise Exception('unknown version')
    else:
        print(config_version)
