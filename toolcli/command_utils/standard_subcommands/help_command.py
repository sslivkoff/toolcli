"""print help of a root command, lists out subcommands and their descriptions"""

from __future__ import annotations

import toolcli
from toolcli.command_utils import help_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': help_command,
        'help': 'output help',
        'args': [
            {'name': 'subcommand', 'nargs': '*'},
            {'name': ['-h', '--help'], 'action': 'store_true'},
            {'name': '--hidden', 'action': 'store_true'},
        ],
        'extra_data': ['parse_spec'],
    }


def help_command(subcommand, help: bool, parse_spec: toolcli.ParseSpec, hidden: bool) -> None:
    if len(subcommand) == 0:
        help_utils.print_root_command_help(parse_spec, show_hidden=hidden)
    else:
        command_sequence = tuple(subcommand)
        command_index = parse_spec['command_index']
        command_spec_reference = command_index.get(command_sequence)
        if command_spec_reference is not None:
            command_spec = toolcli.resolve_command_spec(command_spec_reference)
            sub_parse_spec = {
                'command_spec': command_spec,
                'command_sequence': tuple(subcommand),
                'command_index': parse_spec.get('command_index'),
                'config': parse_spec.get('config')
            }
            help_utils.print_subcommand_help(sub_parse_spec)
        else:
            length = len(command_sequence)
            prefix_of = [
                other_command_sequence
                for other_command_sequence in command_index.keys()
                if other_command_sequence[:length] == command_sequence
            ]
            if len(prefix_of) > 0:
                help_utils.print_prefix_help(
                    command_sequence=command_sequence,
                    parse_spec=parse_spec,
                )
