from __future__ import annotations

import argparse
import types
import typing
from typing_extensions import TypedDict

#
# # types
#


class StyleTheme(TypedDict, total=False):
    comment: str
    description: str
    option: str
    metavar: str


ModuleReference = typing.Union[str, types.ModuleType]
FunctionReference = typing.Union[
    typing.Callable,
    typing.Union[ModuleReference, str],
]


NamedAction = typing.Literal[
    'store',
    'store_const',
    'store_true',
    'store_false',
    'append',
    'append_const',
    'count',
    'help',
    'version',
    'extend',  # python 3.8 only
]


class ArgSpec(TypedDict, total=False):
    #
    # special options
    name: typing.Union[str, typing.Sequence[str]]
    completer: typing.Callable
    internal: typing.Optional[bool]
    #
    # standard argparse options
    action: typing.Optional[typing.Union[NamedAction, argparse.Action]]
    nargs: typing.Optional[typing.Union[int, typing.Literal['?', '*', '+']]]
    const: typing.Optional[typing.Any]
    default: typing.Optional[typing.Any]
    type: typing.Optional[typing.Any]
    choices: typing.Optional[typing.Sequence[str]]
    required: typing.Optional[bool]
    help: typing.Optional[str]
    metavar: typing.Optional[str]
    dest: typing.Optional[str]
    version: typing.Optional[str]


class SpecialCommandParams(TypedDict, total=False):
    cd: bool
    include_parse_spec: bool


class CommandSpec(TypedDict, total=False):
    f: typing.Callable[..., typing.Any]
    help: str
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
    #
    # arg parse
    base_command: str
    description: str
    version: str
    arg_parse_mode: typing.Literal[
        None,
        'known',
        'intermixed',
        'known_intermixed',
    ]
    #
    # toolcli
    common_args: list[ArgSpec]
    default_command_sequence: CommandSequence
    command_sequence_aliases: dict[CommandSequence, CommandSequence]
    sort_command_index: bool
    style_theme: StyleTheme
    #
    # middleware
    pre_middlewares: 'MiddlewareSpecs'
    post_middlewares: 'MiddlewareSpecs'
    #
    # default subcommands
    include_cd_subcommand: bool
    cd_dir_getter: typing.Callable[[str], str]
    cd_dir_help: dict[str, str]
    include_help_subcommand: bool
    include_version_subcommand: bool
    #
    # standard args
    include_debug_arg: bool


default_config: CLIConfig = {
    'sort_command_index': True,
}


standard_args: dict[str, ArgSpec] = {
    'debug': {
        'name': '--debug',
        'help': 'enter debugger if an error occurs',
        'action': 'store_true',
        'internal': True,
    },
    'help': {
        'name': '--help',
        'help': 'output help message',
        'action': 'store_true',
        'internal': True,
    },
    'cd': {
        'name': '--new_dir_tempfile',
        'help': 'used internally by cd command to track destination dir',
        'internal': True,
    },
}


def create_config(config: typing.Optional[CLIConfig] = None) -> CLIConfig:
    import copy

    if config is None:
        config = {}
    new_config = copy.copy(default_config)
    new_config.update(config)
    return new_config

