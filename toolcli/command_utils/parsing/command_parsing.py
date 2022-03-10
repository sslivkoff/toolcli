from __future__ import annotations

import importlib
import typing

import copy
import types
import sys

from toolcli import spec


def create_parse_spec(
    raw_command: typing.Optional[spec.RawCommand],
    command_index: typing.Optional[spec.CommandIndex],
    command_sequence: typing.Optional[spec.CommandSequence],
    command_spec: typing.Optional[spec.CommandSpec],
    config: spec.CLIConfig,
) -> spec.ParseSpec:
    """create ParseSpec data"""

    # get command spec
    if command_spec is None:

        # add default subcommands
        if command_index is None:
            raise Exception('must specify command_spec or command_index')
        command_index = _add_default_subcommands(command_index, config)

        # get command sequence
        if command_sequence is None:
            if raw_command is None:
                raise Exception('must specify command_sequence or raw_command')
            command_sequence = parse_command_sequence(
                raw_command=raw_command,
                command_index=command_index,
                config=config,
            )

        # resolve command spec
        command_spec = resolve_command_spec(command_index[command_sequence])

    parse_spec: spec.ParseSpec = {
        'command_index': command_index,
        'command_sequence': command_sequence,
        'command_spec': command_spec,
        'config': config,
    }

    return parse_spec


def _add_default_subcommands(
    command_index: spec.CommandIndex, config: spec.CLIConfig
) -> spec.CommandIndex:
    """add default subcommands to command_index according to config"""

    command_index = copy.copy(command_index)

    # add version subcommand
    if (
        config.get('include_version_subcommand')
        and ('version',) not in command_index
    ):
        command_index[
            ('version',)
        ] = 'toolcli.command_utils.default_subcommands.version_command'

    # add help subcommand
    if config.get('include_help_subcommand') and ('help',) not in command_index:
        command_index[
            ('help',)
        ] = 'toolcli.command_utils.default_subcommands.help_command'

    # add cd subcommand
    if config.get('include_cd_subcommand') and ('cd',) not in command_index:
        command_index[
            ('cd',)
        ] = 'toolcli.command_utils.default_subcommands.cd_command'

    return command_index


def parse_command_sequence(
    raw_command: spec.RawCommand,
    command_index: spec.CommandIndex,
    config: spec.CLIConfig,
) -> spec.CommandSequence:
    """parse a command sequence from a raw command according to command_index"""

    # parse sequence from args that do not start with '-'
    if isinstance(raw_command, str):
        args = raw_command.split(' ')
        args = [arg.strip() for arg in args]
    elif isinstance(raw_command, list):
        args = raw_command
    else:
        raise Exception(
            'unknown type for raw_command: ' + str(type(raw_command))
        )
    args = [arg for arg in args if not arg.startswith('-')]

    # sort command sequences from longest to shortest
    sequences = list(command_index.keys())
    for sequence in sequences:
        if not isinstance(sequence, tuple):
            raise Exception(
                'sequences should be tuples of str\'s, got: ' + str(sequence)
            )
    if config.get(
        'sort_command_index', spec.default_config['sort_command_index']
    ):
        sequences = sorted(sequences, key=lambda sequence: -len(sequence))
    else:
        sequences = list(sequences)

    # find first command sequence to match
    for sequence in sequences:
        length = len(sequence)
        if sequence == tuple(args[:length]):
            return sequence

    # if not matches, return default command sequence
    default_command_sequence = config.get('default_command_sequence')
    if default_command_sequence is not None:
        return default_command_sequence
    else:
        print(sys.argv)
        print(raw_command)
        print(sequences)
        print(args)
        raise Exception('could not parse command sequence')


def resolve_command_spec(
    command_spec_ref: spec.CommandSpecReference,
) -> spec.CommandSpec:
    """return the command spec referred to by command_spec_ref"""
    if isinstance(command_spec_ref, types.ModuleType):
        if hasattr(command_spec_ref, 'get_command_spec'):
            f = getattr(command_spec_ref, 'get_command_spec')
            return f()
        else:
            raise Exception('module has no function get_command_spec()')
    elif isinstance(command_spec_ref, types.FunctionType):
        return command_spec_ref()
    elif isinstance(command_spec_ref, dict):
        return command_spec_ref
    elif isinstance(command_spec_ref, str):
        module = importlib.import_module(command_spec_ref)
        if hasattr(module, 'get_command_spec'):
            f = getattr(module, 'get_command_spec')
            return f()
        else:
            raise Exception('module has no function get_command_spec()')
    else:
        raise Exception(
            'could not parse command spec: ' + str(command_spec_ref)
        )

