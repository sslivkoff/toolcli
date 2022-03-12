import rich

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': config_command,
        'help': 'print cli config',
        'special': {
            'include_parse_spec': True,
            'hidden': True,
        },
    }


def config_command(parse_spec: toolcli.ParseSpec) -> None:
    config = parse_spec['config']
    rich.print(config)

