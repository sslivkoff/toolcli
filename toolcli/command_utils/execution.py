from __future__ import annotations

import asyncio
import inspect
import importlib
import sys
import typing
import types

from .. import spec
from . import parsing


def run_cli(
    raw_command: typing.Optional[spec.RawCommand] = None,
    command_index: typing.Optional[spec.CommandIndex] = None,
    command_sequence: typing.Optional[spec.CommandSequence] = None,
    command_spec: typing.Optional[spec.CommandSpec] = None,
    config: typing.Optional[spec.CLIConfig] = None,
    args: typing.Optional[dict[str, typing.Any]] = None,
) -> None:

    # create config
    config = spec.create_config(config)

    # create parse spec
    parse_spec = parsing.create_parse_spec(
        raw_command=raw_command,
        command_index=command_index,
        command_sequence=command_sequence,
        command_spec=command_spec,
        config=config,
    )

    # parse args
    args = parsing.parse_args(
        raw_command=parse_spec['raw_command'],
        command_spec=parse_spec['command_spec'],
        config=config,
        parse_spec=parse_spec,
        args=args,
    )

    # execute command_spec and middlewares
    execute(parse_spec=parse_spec, args=args)


def execute(parse_spec: spec.ParseSpec, args: spec.ParsedArgs) -> None:

    # execute pre middleware
    config = parse_spec['config']
    if config.get('pre_middlewares') is not None:
        _execute_middlewares(config['pre_middlewares'], parse_spec, args)

    # gather function args
    function_args = parsing.get_function_args(parse_spec, args)

    # execute command
    command_function = resolve_function(parse_spec['command_spec']['f'])
    debug = bool(config.get('include_debug_arg') and args.get('debug'))
    _execute_function(
        function=command_function,
        args=function_args,
        debug=debug,
    )

    # execute post middleware
    if config.get('post_middlewares') is not None:
        _execute_middlewares(config['post_middlewares'], parse_spec, args)


def _execute_function(
    function: typing.Callable, args: dict, debug: bool
) -> None:

    if not inspect.iscoroutinefunction(function):

        # execute as normal function
        if not debug:
            function(**args)
        else:
            try:
                function(**args)
            except Exception:
                _enter_debugger()
    else:

        # execute as coroutine
        if not debug:
            asyncio.run(function(**args))
        else:
            try:
                asyncio.run(function(**args))
            except Exception:
                _enter_debugger()


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
        f = resolve_function(middleware)

        if inspect.iscoroutinefunction(f):
            asyncio.run(f(parse_spec=parse_spec, args=args))
        else:
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

