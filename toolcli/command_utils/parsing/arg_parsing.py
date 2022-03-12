from __future__ import annotations

import argparse
import copy
import typing

from toolcli import spec
from .. import help_utils


class SubcommandArgumentParser(argparse.ArgumentParser):
    """subclass of argparse.ArgumentParser that stores current ParseSpec"""

    def __init__(
        self: SubcommandArgumentParser,
        parse_spec: spec.ParseSpec,
        **kwargs: typing.Any,
    ):
        self.parse_spec = parse_spec
        super().__init__(**kwargs)

    def print_usage(
        self,
        file: typing.Optional[typing.IO[str]] = None,
    ) -> None:
        help_utils.print_subcommand_usage(self.parse_spec)

    def print_help(
        self,
        file: typing.Optional[typing.IO[str]] = None,
    ) -> None:
        if self.parse_spec['command_sequence'] == ():
            help_utils.print_root_command_help(self.parse_spec)
        else:
            help_utils.print_subcommand_help(self.parse_spec)


def parse_raw_command(
    raw_command: spec.RawCommand, parse_spec: spec.ParseSpec
) -> spec.ParsedArgs:
    """parse command args from raw_command according to command_spec"""

    config = parse_spec.get('config')
    if config is None:
        config = spec.create_config(config)

    # gather arg specs
    command_spec = parse_spec['command_spec']
    arg_specs = command_spec.get('args', [])
    arg_specs += config.get('common_args', [])
    if config.get('include_debug_arg'):
        arg_specs.append(spec.standard_args['debug'])
    if config.get('include_cd_subcommand'):
        arg_specs.append(spec.standard_args['cd'])

    # create parser
    parser = SubcommandArgumentParser(
        parse_spec=parse_spec,
        description=config.get('description'),
        prog=config.get('base_command', '<program>'),
    )

    # add arguments
    for arg_spec in arg_specs:

        # get name args
        name = arg_spec.get('name')
        if isinstance(name, str):
            name_args = [name]
        elif isinstance(name, list):
            name_args = name
        else:
            raise Exception('unknown name format: ' + str(name))

        # remove special options
        kwargs = copy.copy(arg_spec)
        kwargs.pop('name')
        kwargs.pop('completer', None)
        kwargs.pop('internal', None)

        # add argument to parser
        kwargs = typing.cast(
            spec.ArgSpec, {k: v for k, v in kwargs.items() if v is not None}
        )
        parser.add_argument(*name_args, **kwargs)  # type: ignore

    # remove command sequence from raw command
    if isinstance(raw_command, str):
        raw_command = [
            token.strip() for token in raw_command.split(' ') if token != ''
        ]
    raw_command = list(raw_command)
    command_sequence = parse_spec.get('command_sequence')
    if command_sequence is not None:
        for token in command_sequence:
            if token in raw_command:
                raw_command.pop(raw_command.index(token))
            else:
                break

    # tokenize raw command
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

    return parsed_args


def get_arg_name(arg_spec: spec.ArgSpec) -> str:
    """get name of an argument according to an ArgSpec"""

    if isinstance(arg_spec['name'], str):
        return arg_spec['name'].strip('-')
    else:
        for name in arg_spec['name']:
            if name[0] != '-' or name.startswith('--'):
                return name.strip('-')
        else:
            raise Exception('could not determine argument name')


def is_arg_optional(arg_spec: spec.ArgSpec) -> bool:
    """return whether arg is optional"""

    if arg_spec.get('required'):
        return False
    else:
        if isinstance(arg_spec['name'], str) and arg_spec['name'].startswith(
            '-'
        ):
            return True
        else:
            return all(name.startswith('-') for name in arg_spec['name'])


def get_function_args(
    parse_spec: spec.ParseSpec, args: dict[typing.Any, typing.Any]
) -> dict[typing.Any, typing.Any]:
    """extract subset of parsed cli args that are passed to command function"""

    config = parse_spec['config']
    command_spec = parse_spec['command_spec']
    special = command_spec.get('special', {})

    # build function kwargs
    function_args = {}
    for arg_spec in command_spec.get('args', []):
        name = get_arg_name(arg_spec)
        name = name.replace('-', '_')

        if arg_spec.get('internal'):
            # skip special args
            continue

        elif name in args:
            # add argument if it is specified in args
            function_args[name] = args[name]

        elif is_arg_optional(arg_spec):
            # add default value if argument is optional
            if 'default' in arg_spec:
                function_args[name] = arg_spec['default']
            elif arg_spec.get('action') == 'store_true':
                function_args[name] = False
            elif arg_spec.get('action') == 'store_false':
                function_args[name] = True
            else:
                function_args[name] = None

        else:
            raise Exception('must specify arg: ' + str(name))

    # special arg: cd
    # include cd kwarg if using using cd
    if config['include_cd_subcommand'] and command_spec.get('special', {}).get(
        'cd'
    ):
        cd_arg_name = get_arg_name(spec.standard_args['cd'])
        function_args[cd_arg_name] = args.get(cd_arg_name)

    # special arg: parse_spec
    # include parse spec
    if special.get('include_parse_spec'):
        function_args['parse_spec'] = parse_spec

    return function_args

