from __future__ import annotations

import types
import typing
from typing_extensions import TypedDict

#
# # types
#

ModuleReference = typing.Union[str, types.ModuleType]
FunctionReference = typing.Union[
    typing.Callable,
    typing.Union[ModuleReference, str],
]


class ArgSpec(TypedDict, total=False):
    name: typing.Union[str, list[str]]
    kwargs: dict[str, typing.Any]
    completer: typing.Callable


class SpecialCommandParams(TypedDict, total=False):
    cd: bool


class CommandSpec(TypedDict):
    f: typing.Callable[..., typing.Any]
    args: list[ArgSpec]
    special: SpecialCommandParams


CommandSequence = typing.Tuple[str, ...]
CommandSpecReference = typing.Union[
    CommandSpec,
    ModuleReference,
    FunctionReference,
]

CommandIndex = typing.Dict[CommandSequence, CommandSpecReference]

RawCommand = typing.Union[str, typing.List[str]]


class ParseSpec(TypedDict):
    raw_command: typing.Optional[RawCommand]
    command_index: typing.Optional[CommandIndex]
    command_sequence: typing.Optional[CommandSequence]
    command_spec: CommandSpec
    config: 'CLIConfig'


ParsedArgs = typing.Dict[str, typing.Any]

# the first argument to MiddlewareFunction should be CLIState
# however, mypy does not currently support recursive types
# see https://github.com/python/mypy/issues/731
MiddlewareFunction = typing.Callable[[typing.Any, ParsedArgs], None]

MiddlewareSpec = typing.Union['MiddlewareFunction', FunctionReference]
MiddlewareSpecs = typing.List['MiddlewareSpec']


class CLIConfig(TypedDict, total=False):
    description: str
    common_args: list[ArgSpec]
    default_command_sequence: CommandSequence
    command_sequence_aliases: dict[CommandSequence, CommandSequence]
    sort_command_index: bool
    pre_middlewares: 'MiddlewareSpecs'
    post_middlewares: 'MiddlewareSpecs'
    include_debug_arg: bool
    include_help_arg: bool
    inject_parse_spec: bool
    arg_parse_mode: typing.Literal[
        None,
        'known',
        'intermixed',
        'known_intermixed',
    ]
    include_cd: bool


default_config: CLIConfig = {
    'sort_command_index': True,
}


standard_args: dict[str, ArgSpec] = {
    'debug': {'name': ['--debug', '-d'], 'kwargs': {'action': 'store_true'}},
    'help': {'name': '--help', 'kwargs': {'action': 'store_true'}},
    'cd': {'name': '--new_dir_tempfile'},
}


def build_config(config: typing.Optional[CLIConfig] = None) -> CLIConfig:
    import copy

    if config is None:
        config = {}
    new_config = copy.copy(default_config)
    new_config.update(config)
    return new_config

