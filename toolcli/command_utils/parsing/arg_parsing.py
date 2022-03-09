from __future__ import annotations

import argparse
import copy
import typing

from toolcli import spec


class SubcommandArgumentParser(argparse.ArgumentParser):
    def print_usage(self, file=None):
        print('USAGE')

    def print_help(self, file=None):
        print('HELP')


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

    if config is None:
        config = spec.build_config(config)

    # create parser
    parser = SubcommandArgumentParser(
        description=config.get('description'),
        add_help=False,
        prog=config.get('base_command', '<program>'),
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
        kwargs = copy.copy(arg_spec)
        kwargs.pop('name')
        if 'completer' in kwargs:
            kwargs.pop('completer')
        kwargs = typing.cast(
            spec.ArgSpec, {k: v for k, v in kwargs.items() if v is not None}
        )
        parser.add_argument(*name_args, **kwargs)  # type: ignore

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

    if config.get('inject_parse_spec') or command_spec.get('special', {}).get(
        'parse_spec'
    ):
        if 'parse_spec' in parsed_args:
            raise Exception('key collision: cli')
        parsed_args['parse_spec'] = parse_spec

    return parsed_args

