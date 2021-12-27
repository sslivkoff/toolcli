import types
import typing

#
# # types
#

ModuleReference = typing.Union[str, types.ModuleType]
FunctionReference = typing.Union[
    typing.Callable,
    typing.Union[ModuleReference, str],
]


class ArgSpec(typing.TypedDict, total=False):
    name: typing.Union[str, list[str]]
    kwargs: dict[str, typing.Any]
    completer: typing.Callable


class CommandSpec(typing.TypedDict):
    f: typing.Callable[..., typing.Any]
    args: list[ArgSpec]


CommandSequence = typing.Tuple[str, ...]
CommandSpecReference = typing.Union[
    CommandSpec,
    ModuleReference,
    FunctionReference,
]

CommandIndex = dict[CommandSequence, CommandSpecReference]

RawCommand = typing.Union[str, list[str]]


class ParseSpec(typing.TypedDict):
    raw_command: typing.Optional[RawCommand]
    command_index: typing.Optional[CommandIndex]
    command_sequence: typing.Optional[CommandSequence]
    command_spec: CommandSpec
    config: 'CLIConfig'


ParsedArgs = dict[str, typing.Any]

# the first argument to MiddlewareFunction should be CLIState
# however, mypy does not currently support recursive types
# see https://github.com/python/mypy/issues/731
MiddlewareFunction = typing.Callable[[typing.Any, ParsedArgs], None]

MiddlewareSpec = typing.Union['MiddlewareFunction', FunctionReference]
MiddlewareSpecs = list['MiddlewareSpec']


class CLIConfig(typing.TypedDict, total=False):
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


default_config: CLIConfig = {
    'sort_command_index': True,
}


standard_args: dict[str, ArgSpec] = {
    'debug': {'name': ['--debug', '-d'], 'kwargs': {'action': 'store_true'}},
    'help': {'name': '--help', 'kwargs': {'action': 'store_true'}},
}


def build_config(config: typing.Optional[CLIConfig] = None) -> CLIConfig:
    import copy

    if config is None:
        config = {}
    new_config = copy.copy(default_config)
    new_config.update(config)
    return new_config

