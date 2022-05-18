from __future__ import annotations

import inspect

import toolcli
from toolcli.command_utils import parsing


def annotate_command_spec(command_spec: toolcli.CommandSpec) -> str:
    """return the type-annotated function definition of a command function"""

    # keywords
    annotated = ''
    f = command_spec['f']
    if inspect.iscoroutinefunction(f):
        annotated += 'async '
    annotated += 'def '

    # name and arguments
    annotated += f.__name__ + '('
    for arg in command_spec.get('args', []):
        if arg.get('action') in ['store_true', 'store_false']:
            arg_type = 'bool'
        elif arg.get('type') is not None:
            type_object = arg['type']
            if type_object is None:
                raise Exception('could not determine type')
            arg_type = type_object.__name__
        elif arg.get('nargs') is not None and arg.get('nargs') != 1:
            arg_type = 'typing.Sequence[str]'
        else:
            arg_type = 'str'

        if parsing.is_arg_optional(arg):
            arg_type = 'typing.Optional[' + arg_type + ']'

        arg_name = parsing.get_arg_name(arg)
        arg_name = arg_name.replace('-', '_')

        annotated += (
            '\n    ' + arg_name + ': ' + arg_type + ','
        )
    annotated += '\n) -> None:'
    return annotated

