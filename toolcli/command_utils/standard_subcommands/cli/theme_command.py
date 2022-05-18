from __future__ import annotations

import typing

import rich

import toolcli
from toolcli import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': theme_command,
        'help': 'display cli style theme',
        'hidden': True,
        'extra_data': ['parse_spec'],
    }


def theme_command(parse_spec: spec.ParseSpec) -> None:
    config = parse_spec.get('config')
    if config is None:
        print('no theme')
    else:
        theme = config.get('style_theme')
        if theme is None:
            print('no theme')
        else:
            longest = max(len(key) for key in theme.keys())
            longest = longest + 1
            for key, value in theme.items():
                value_str = typing.cast(str, value)
                rich.print(
                    (key + ':').ljust(longest)
                    + '  '
                    + '['
                    + value_str
                    + ']'
                    + value_str
                    + '[/'
                    + value_str
                    + ']',
                )
