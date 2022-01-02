import importlib
import os
import sys
import types
import typing

from . import spec


def build_parse_spec(
    raw_command: typing.Optional[spec.RawCommand],
    command_index: typing.Optional[spec.CommandIndex],
    command_sequence: typing.Optional[spec.CommandSequence],
    command_spec: typing.Optional[spec.CommandSpec],
    config: spec.CLIConfig,
) -> spec.ParseSpec:

    # get command spec
    if command_spec is None:

        if command_index is None:
            raise Exception('must specify command_spec or command_index')

        if raw_command is None:
            raw_command = sys.argv[1:]

        # get command sequence
        if command_sequence is None:
            command_sequence = parse_command_sequence(
                raw_command=raw_command,
                command_index=command_index,
                config=config,
            )

        # remove command sequence
        if isinstance(raw_command, str):
            raw_command = [
                token.strip() for token in raw_command.split(' ') if token != ''
            ]
        raw_command = list(raw_command)
        for token in command_sequence:
            raw_command.pop(raw_command.index(token))

        command_spec = resolve_command_spec(command_index[command_sequence])

    parse_spec: spec.ParseSpec = {
        'raw_command': raw_command,
        'command_index': command_index,
        'command_sequence': command_sequence,
        'command_spec': command_spec,
        'config': config,
    }

    return parse_spec


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


def resolve_function(
    function_ref: spec.FunctionReference,
) -> types.FunctionType:
    """return the function refered to by function_ref"""

    if isinstance(function_ref, types.FunctionType):
        return function_ref
    elif isinstance(function_ref, (list, tuple)):
        module_name, function_name = function_ref
        module = importlib.import_module(module_name)
        return getattr(module, function_name)
    else:
        raise Exception(
            'could not parse command function: ' + str(function_ref)
        )


def parse_args(
    args: typing.Optional[spec.ParsedArgs],
    raw_command: typing.Optional[spec.RawCommand],
    command_spec: spec.CommandSpec,
    config: typing.Optional[spec.CLIConfig] = None,
    parse_spec: typing.Optional[spec.ParseSpec] = None,
) -> spec.ParsedArgs:

    if args is not None:
        return dict(args)
    else:
        if raw_command is None:
            raise Exception('must specify raw_command or args')
        return parse_raw_command(
            raw_command=raw_command,
            command_spec=command_spec,
            config=config,
            parse_spec=parse_spec,
        )


def parse_raw_command(
    raw_command: spec.RawCommand,
    command_spec: spec.CommandSpec,
    config: typing.Optional[spec.CLIConfig] = None,
    parse_spec: typing.Optional[spec.ParseSpec] = None,
) -> spec.ParsedArgs:
    """parse command args from raw_command according to command_spec"""

    import argparse

    if config is None:
        config = spec.build_config(config)

    # create parser
    parser = argparse.ArgumentParser(
        description=config.get('description'),
    )

    # gather arg specs
    arg_specs = command_spec.get('args', [])
    arg_specs += config.get('common_args', [])
    if config.get('include_debug_arg'):
        arg_specs.append(spec.standard_args['debug'])
    if config.get('include_help_arg'):
        arg_specs.append(spec.standard_args['help'])
    if config.get('include_cd'):
        arg_specs.append(spec.standard_args['cd'])

    # add arguments
    for arg_spec in arg_specs:
        name = arg_spec.get('name')
        if isinstance(name, str):
            name_args = [name]
        elif isinstance(name, list):
            name_args = name
        else:
            raise Exception('unknown name format: ' + str(name))
        parser.add_argument(*name_args, **arg_spec.get('kwargs', {}))

    if isinstance(raw_command, str):
        raw_args = [arg.strip() for arg in raw_command.split(' ')]
    elif isinstance(raw_command, list):
        raw_args = raw_command
    else:
        raise Exception(
            'unknown type for raw_command: ' + str(type(raw_command))
        )

    # parse arguments
    parse_mode = config.get('parse_mode')
    if parse_mode is None:
        args = parser.parse_args(args=raw_args)
    elif parse_mode == 'known':
        args, _ = parser.parse_known_args(args=raw_args)
    elif parse_mode == 'intermixed':
        args = parser.parse_intermixed_args(args=raw_args)
    elif parse_mode == 'known_intermixed':
        args, _ = parser.parse_known_intermixed_args(args=raw_args)
    else:
        raise Exception('unknown parse_mode: ' + str(parse_mode))

    parsed_args = vars(args)

    if config.get('inject_parse_spec'):
        if 'parse_spec' in parsed_args:
            raise Exception('key collision: cli')
        parsed_args['parse_spec'] = parse_spec

    return parsed_args


#
# # command index manipulation
#


def add_command_sequence_aliases(
    command_index: spec.CommandIndex,
    config: spec.CLIConfig,
) -> spec.CommandIndex:
    command_sequence_aliases = config.get('command_sequence_aliases')
    if command_sequence_aliases is not None:

        # add aliases to command index
        command_index = dict(command_index)
        for sequence, spec_ref in command_index.items():
            for alias in command_sequence_aliases:
                if sequence[: len(alias)] == alias:
                    len_alias = len(alias)
                    alias_command = alias + sequence[len_alias:]
                    if alias_command not in command_index:
                        command_index[alias_command] = command_index[sequence]

    return command_index


def filetree_to_command_index(
    root_module_name: str,
    postfix: str = '_command.py',
) -> spec.CommandIndex:

    import inspect

    if not postfix.endswith('.py'):
        raise Exception('postfix must end with ".py"')

    command_sequences: list[spec.CommandSequence] = []
    modules = []

    # add root node if it has a get_command_spec attribute
    root_module = importlib.import_module(root_module_name)
    if hasattr(root_module, 'get_command_spec'):
        command_sequences.append(tuple())
        modules.append(root_module_name)

    root_module_path = os.path.dirname(inspect.getfile(root_module))
    for dirname, subdirs, files in os.walk(root_module_path):
        for file in files:
            if file.endswith(postfix):

                relpath = os.path.relpath(dirname, root_module_path)

                command_name = file[: -len(postfix)]
                as_list = relpath.split(os.path.sep) + [command_name]
                command_sequence = tuple(as_list)

                relmodule = relpath.replace(os.path.sep, '.')
                module_name = file[:-3]
                module_ref = (
                    root_module_name + '.' + relmodule + '.' + module_name
                )

                command_sequences.append(command_sequence)
                modules.append(module_ref)

    command_index: spec.CommandIndex = dict(zip(command_sequences, modules))

    return command_index

