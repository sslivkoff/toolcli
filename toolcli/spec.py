from __future__ import annotations

import argparse
import types
import typing
from typing_extensions import TypedDict, Literal, Protocol

#
# # types
#


class StyleTheme(TypedDict, total=False):
    title: str
    comment: str
    description: str
    option: str
    metavar: str


ModuleReference = typing.Union[str, types.ModuleType]
FunctionReference = typing.Union[
    typing.Callable[..., typing.Any],
    typing.Union[ModuleReference, str],
]


NamedAction = Literal[
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
    completer: typing.Callable[..., typing.Any]
    internal: typing.Optional[bool]
    #
    # standard argparse options
    action: typing.Optional[typing.Union[NamedAction, argparse.Action]]
    nargs: typing.Optional[typing.Union[int, Literal['?', '*', '+']]]
    const: typing.Optional[typing.Any]
    default: typing.Optional[typing.Any]
    type: typing.Optional[typing.Any]
    choices: typing.Optional[typing.Sequence[str]]
    required: typing.Optional[bool]
    help: typing.Optional[str]
    metavar: typing.Optional[str]
    dest: typing.Optional[str]
    version: typing.Optional[str]


class CallExample(TypedDict, total=False):
    description: str
    runnable: bool


# because mypy cannot express cyclic types...
# help: typing.Union[str, typing.Callable[['ParseSpec'], str]]


class CommandSpec(TypedDict, total=False):
    f: typing.Callable[..., typing.Any]
    help: typing.Union[str, typing.Callable[[typing.Any], str]]
    args: typing.Sequence[ArgSpec]
    examples: typing.Sequence[str] | typing.Mapping[str, str | CallExample]
    hidden: bool
    extra_data: typing.Sequence[str]


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


class HelpUrlGetter(Protocol):
    def __call__(
        self,
        *,
        subcommand: typing.Tuple[str, ...],
        parse_spec: 'ParseSpec',
    ) -> str:
        pass


class Plugin(TypedDict, total=False):
    command_index: CommandIndex
    required_extra_data: typing.Sequence[str]
    help_category: str


class CLIConfig(TypedDict, total=False):
    #
    # arg parse
    base_command: str
    description: str
    version: str
    arg_parse_mode: Literal[
        None,
        'known',
        'intermixed',
        'known_intermixed',
    ]
    async_context_manager: typing.Callable[
        ..., typing.AsyncContextManager[typing.Any]
    ]
    #
    # toolcli
    default_command_sequence: CommandSequence
    command_sequence_aliases: dict[CommandSequence, CommandSequence]
    sort_command_index: bool
    style_theme: StyleTheme
    extra_data: typing.Mapping[str, typing.Any]
    extra_data_getters: typing.Mapping[str, typing.Callable[..., typing.Any]]
    plugins: typing.Sequence[Plugin]
    #
    # middleware
    pre_middlewares: 'MiddlewareSpecs'
    post_middlewares: 'MiddlewareSpecs'
    #
    # default subcommands
    include_standard_subcommands: bool | typing.Sequence[typing.Sequence[str]]
    cd_dir_getter: typing.Callable[[str], str]
    cd_dir_help: dict[str, str]
    help_url_getter: HelpUrlGetter
    help_cache_dir: str | None
    help_subcommand_categories: typing.MutableMapping[CommandSequence, str]
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
        'name': '--cd-destination-tempfile',
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
