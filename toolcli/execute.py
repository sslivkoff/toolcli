from __future__ import annotations

import asyncio
import inspect
import sys
import typing
import types

from . import spec
from . import parse


def run_cli(
    raw_command: typing.Optional[spec.RawCommand] = None,
    command_index: typing.Optional[spec.CommandIndex] = None,
    command_sequence: typing.Optional[spec.CommandSequence] = None,
    command_spec: typing.Optional[spec.CommandSpec] = None,
    config: typing.Optional[spec.CLIConfig] = None,
    args: typing.Optional[dict[str, typing.Any]] = None,
) -> None:

    # build config
    config = spec.build_config(config)

    # build parse spec
    parse_spec = parse.build_parse_spec(
        raw_command=raw_command,
        command_index=command_index,
        command_sequence=command_sequence,
        command_spec=command_spec,
        config=config,
    )

    # parse args
    args = parse.parse_args(
        raw_command=parse_spec['raw_command'],
        command_spec=parse_spec['command_spec'],
        config=config,
        parse_spec=parse_spec,
        args=args,
    )

    # execute command_spec and middlewares
    _execute(parse_spec=parse_spec, args=args)


def _execute(parse_spec: spec.ParseSpec, args: spec.ParsedArgs) -> None:

    # execute pre middleware
    config = parse_spec['config']
    if config.get('pre_middlewares') is not None:
        _execute_middlewares(config['pre_middlewares'], parse_spec, args)

    # remove cd arg if not using cd
    command_spec = parse_spec['command_spec']
    if config['include_cd'] and not command_spec.get('special', {}).get('cd'):
        cd_arg_name = spec.standard_args['cd']['name']
        if isinstance(cd_arg_name, str):
            args.pop(cd_arg_name.strip('-'))
        else:
            raise Exception('multiple names for cd arg')

    # execute command
    command_function = parse.resolve_function(command_spec['f'])
    debug = config.get('include_debug_option') and args.get('debug')
    if not inspect.iscoroutinefunction(command_function):
        if not debug:
            command_function(**args)
        else:
            try:
                command_function(**args)
            except Exception:
                _enter_debugger()
    else:
        if not debug:
            asyncio.run(command_function(**args))
        else:
            try:
                asyncio.run(command_function(**args))
            except Exception:
                _enter_debugger()

    # execute post middleware
    if config.get('post_middlewares') is not None:
        _execute_middlewares(config['post_middlewares'], parse_spec, args)


def _enter_debugger() -> None:
    """open debugger to most recent exception

    - adapted from https://stackoverflow.com/a/242514
    """

    import traceback

    # print stacktrace
    extype, value, tb = sys.exc_info()
    print('[ENTERING DEBUGGER]')
    traceback.print_exc()
    print()

    try:
        import ipdb

        tb = typing.cast(types.TracebackType, tb)
        ipdb.post_mortem(tb)

    except ImportError:
        import pdb

        pdb.post_mortem(tb)


def _execute_middlewares(
    middlewares: list[spec.MiddlewareSpec],
    parse_spec: spec.ParseSpec,
    args: spec.ParsedArgs,
) -> None:
    for middleware in middlewares:
        f = parse.resolve_function(middleware)
        f(parse_spec=parse_spec, args=args)


def execute_other_command_sequence(
    command_sequence: spec.CommandSequence,
    parse_spec: spec.ParseSpec,
    args: dict[str, typing.Any] = None,
) -> None:
    """execute a command sequence from within another command function"""
    run_cli(
        raw_command=parse_spec['raw_command'],
        command_sequence=command_sequence,
        command_index=parse_spec['command_index'],
        config=parse_spec['config'],
        args=args,
    )


def execute_other_command_spec(
    command_spec: spec.CommandSpec,
    parse_spec: spec.ParseSpec,
    args: typing.Optional[spec.ParsedArgs] = None,
) -> None:
    """execute a command spec from within another command function"""
    run_cli(
        command_spec=command_spec,
        raw_command=parse_spec['raw_command'],
        config=parse_spec['config'],
        args=args,
    )

