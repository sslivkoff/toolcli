from __future__ import annotations

import importlib
import sys
import typing
import types

from .. import spec
from . import parsing


def run_cli(
    raw_command: typing.Optional[spec.RawCommand] = None,
    command_sequence: typing.Optional[spec.CommandSequence] = None,
    command_index: typing.Optional[spec.CommandIndex] = None,
    command_spec: typing.Optional[spec.CommandSpec] = None,
    args: typing.Optional[spec.ParsedArgs] = None,
    config: typing.Optional[spec.CLIConfig] = None,
) -> None:
    """run cli

    Requires at least one of the following sets of arguments:
    - {raw_command, command_index}
    - {args, command_sequence, command_index}
    - {raw_command, command_spec}
    - {args, command_spec}
    """

    # create config
    config = spec.create_config(config)

    # get raw command
    if raw_command is None and command_sequence is None:
        raw_command = sys.argv[1:]

    # create parse spec
    parse_spec = parsing.create_parse_spec(
        raw_command=raw_command,
        command_index=command_index,
        command_sequence=command_sequence,
        command_spec=command_spec,
        config=config,
    )

    # parse args
    if args is None:
        if raw_command is None:
            raise Exception('must specify raw_command or args')
        args = parsing.parse_raw_command(
            raw_command=raw_command,
            parse_spec=parse_spec,
        )

    # execute command_spec and middlewares
    try:
        execute_parsed_command(parse_spec=parse_spec, args=args)
    except Exception as exception:
        if args.get('debug'):
            _enter_debugger()
        else:
            if len(exception.args) == 0:
                print('unknown error, use --debug to debug')
            else:
                print(exception.args[0])
            sys.exit()


def execute_parsed_command(
    parse_spec: spec.ParseSpec,
    args: spec.ParsedArgs,
    middleware: bool = True,
) -> None:
    """execute parsed command with specified arguments"""

    # execute pre middleware
    config = parse_spec['config']
    if middleware and config.get('pre_middlewares') is not None:
        _execute_middlewares(config['pre_middlewares'], parse_spec, args)

    # gather function args
    function_args = parsing.get_function_args(parse_spec, args)

    # execute command
    execute_command_spec(
        command_spec=parse_spec['command_spec'],
        args=function_args,
        async_context_manager=config.get('async_context_manager'),
    )

    # execute post middleware
    if middleware and config.get('post_middlewares') is not None:
        _execute_middlewares(config['post_middlewares'], parse_spec, args)


def _iscoroutinefunction(function: typing.Any) -> bool:
    """lightweight version of inspect.iscoroutinefunction()"""

    if not isinstance(function, types.FunctionType):
        return False

    # inspect.CO_COROUTINE
    flag = 128

    return bool(function.__code__.co_flags & flag)


def execute_command_spec(
    command_spec: spec.CommandSpec,
    args: typing.Mapping[str, typing.Any],
    async_context_manager: typing.Callable[
        ..., typing.AsyncContextManager[typing.Any]
    ]
    | None = None,
) -> None:
    """execute command_spec command with specified arguments"""

    function = resolve_function(command_spec['f'])

    if not _iscoroutinefunction(function):
        function(**args)
    else:
        import asyncio

        if async_context_manager is not None:
            coroutine = _async_execute_in_context_manager(
                function,
                args,
                async_context_manager,
            )
            asyncio.run(coroutine)
        else:
            asyncio.run(function(**args))


async def _async_execute_in_context_manager(
    function: typing.Callable[..., typing.Any],
    args: typing.Mapping[str, typing.Any],
    async_context_manager: typing.Callable[
        ..., typing.AsyncContextManager[typing.Any]
    ],
) -> None:
    async with async_context_manager():
        await function(**args)


def resolve_function(
    function_ref: spec.FunctionReference,
) -> types.FunctionType:
    """return the function refered to by function_ref"""

    if isinstance(function_ref, types.FunctionType):
        return function_ref
    elif isinstance(function_ref, (list, tuple)):
        if len(function_ref) not in [1, 2]:
            raise Exception(
                'function reference should be (module_name, function_name)'
            )
        module_name, function_name = function_ref
        module = importlib.import_module(module_name)
        return getattr(module, function_name)
    else:
        raise Exception(
            'could not parse command function: ' + str(function_ref)
        )


def execute_other_command_sequence(
    command_sequence: spec.CommandSequence,
    parse_spec: spec.ParseSpec,
    args: dict[str, typing.Any],
    middleware: bool = False,
) -> None:
    """execute a command sequence from within another command function"""
    command_index = parse_spec['command_index']
    if command_index is None:
        raise Exception('invalid command_index')
    command_spec_reference = command_index[command_sequence]
    command_spec = parsing.resolve_command_spec(command_spec_reference)
    parse_spec = typing.cast(spec.ParseSpec, dict(parse_spec))
    parse_spec['command_sequence'] = command_sequence
    parse_spec['command_spec'] = command_spec
    execute_parsed_command(
        args=args,
        parse_spec=parse_spec,
        middleware=middleware,
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
        import ipdb  # type: ignore

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
    """execute middlewares"""
    for middleware in middlewares:
        f = resolve_function(middleware)

        if _iscoroutinefunction(f):
            import asyncio

            asyncio.run(f(parse_spec=parse_spec, args=args))
        else:
            f(parse_spec=parse_spec, args=args)
