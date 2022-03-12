"""print help of a root command, lists out subcommands and their descriptions"""

from __future__ import annotations

import toolcli
from toolcli.command_utils import help_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': help_command,
        'help': 'output help',
        'special': {
            'include_parse_spec': True,
        },
    }


def help_command(parse_spec: toolcli.ParseSpec) -> None:
    help_utils.print_root_command_help(parse_spec)

