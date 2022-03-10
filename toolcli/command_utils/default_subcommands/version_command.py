from __future__ import annotations

from toolcli import spec


def get_command_spec() -> spec.CommandSpec:
    return {
        'f': version_command,
        'help': 'print cli version',
        'special': {'include_parse_spec': True},
    }


def version_command(parse_spec: spec.ParseSpec) -> None:
    version = parse_spec['config'].get('version')
    if version is None:
        raise Exception('unknown version')
    else:
        print(version)

