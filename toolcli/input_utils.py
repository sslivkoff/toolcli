from __future__ import annotations

import os
import typing
from typing_extensions import Literal, TypedDict
import sys


InvalidAction = Literal['retry', 'exit']


class _InputYesNoKwargs(TypedDict):
    prompt: str
    invalid_action: InvalidAction
    default: typing.Optional[str]
    default_prefix: typing.Optional[str]
    default_postfix: typing.Optional[str]
    add_prompt_symbol: bool
    style: typing.Optional[str]


def input_prompt(
    prompt: str = '',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
    style: typing.Optional[str] = None,
) -> str:

    # add default prompt
    if default is not None:
        if prompt.endswith('\n'):
            if default_prefix is None:
                default_prefix = '\n(default = '
            if default_postfix is None:
                default_postfix = ')\n'
        else:
            if default_prefix is None:
                default_prefix = '(default = '
            if default_postfix is None:
                default_postfix = ') '
        prompt += default_prefix + str(default) + default_postfix
    if prompt.endswith('\n') and add_prompt_symbol:
        prompt += '> '

    # obtain response
    try:
        import rich.console

        if style is not None:
            prompt = '[' + style + ']' + prompt + '[/' + style + ']'

        console = rich.console.Console()
        response = console.input(prompt)
    except KeyboardInterrupt:
        print()
        sys.exit()

    # set default response
    if default is not None and response == '':
        response = default

    return response


def input_int(
    prompt: str = '',
    invalid_action: InvalidAction = 'retry',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
    style: typing.Optional[str] = None,
) -> int:
    recursive_kwargs: _InputYesNoKwargs = {
        'prompt': prompt,
        'invalid_action': invalid_action,
        'default': default,
        'default_prefix': default_prefix,
        'default_postfix': default_postfix,
        'add_prompt_symbol': add_prompt_symbol,
        'style': style,
    }

    answer = input_prompt(
        prompt=prompt,
        default=default,
        default_prefix=default_prefix,
        default_postfix=default_postfix,
        add_prompt_symbol=add_prompt_symbol,
        style=style,
    )

    try:
        return int(answer)
    except ValueError:
        print()
        print('Invalid value')
        print()
        return input_int(**recursive_kwargs)


def input_yes_or_no(
    prompt: str = '',
    invalid_action: InvalidAction = 'retry',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
    style: typing.Optional[str] = None,
) -> bool:

    recursive_kwargs: _InputYesNoKwargs = {
        'prompt': prompt,
        'invalid_action': invalid_action,
        'default': default,
        'default_prefix': default_prefix,
        'default_postfix': default_postfix,
        'add_prompt_symbol': add_prompt_symbol,
        'style': style,
    }

    response = input_prompt(
        prompt=prompt,
        default=default,
        default_prefix=default_prefix,
        default_postfix=default_postfix,
        add_prompt_symbol=add_prompt_symbol,
        style=style,
    )

    # act according to response
    response = response.lower()
    if response in ['y', 'yes']:
        return True
    elif response in ['n', 'no']:
        return False
    elif response == '':
        return input_yes_or_no(**recursive_kwargs)
    else:
        if invalid_action == 'exit':
            print('must enter yes or no')
            sys.exit()
        elif invalid_action == 'retry':
            print('must enter yes or no')
            return input_yes_or_no(**recursive_kwargs)
        else:
            raise Exception('unknown invalid_action: ' + str(invalid_action))


def input_number_choice(
    prompt: typing.Optional[str] = None,
    *,
    choices: list[str],
    invalid_action: InvalidAction = 'retry',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
    style: typing.Optional[str] = None,
) -> int:

    # validate inputs
    if len(set(choices)) != len(choices):
        raise Exception('choices are not unique')
    if default is not None and default not in choices:
        raise Exception('default value must be in choices')

    # build full prompt
    full_prompt = ''
    if prompt is not None:
        full_prompt += prompt + '\n'
    for c, choice in enumerate(choices):
        if default is not None and choice == default:
            choice = choice + ' (default)'
        full_prompt += '    ' + str(c + 1) + '. ' + choice + '\n'

    if default is not None:
        full_prompt += '(default = ' + str(default) + ')\n'

    # select input
    choice = input_prompt(
        prompt=full_prompt,
        default=None,
        add_prompt_symbol=add_prompt_symbol,
        style=style,
    )

    if default is not None and choice == '':
        choice = str(choices.index(default) + 1)

    try:

        # return valid input

        return int(choice) - 1

    except (ValueError, IndexError):

        # handle invalid input

        if invalid_action == 'exit':
            print()
            print('invalid choice')
            sys.exit()

        elif invalid_action == 'retry':
            print('invalid choice')
            return input_number_choice(
                prompt=prompt,
                choices=choices,
                invalid_action=invalid_action,
                default=default,
                default_prefix=default_prefix,
                default_postfix=default_postfix,
                add_prompt_symbol=add_prompt_symbol,
                style=style,
            )

        else:
            raise Exception('unknown invalid_action: ' + str(invalid_action))


def input_first_letter_choice(
    choices: list[str],
    pre_prompt: typing.Optional[str] = None,
    post_prompt: typing.Optional[str] = None,
    default: typing.Optional[str] = None,
    default_prefix: str = '\n\ndefault = ',
    style: typing.Optional[str] = None,
) -> int:

    # validate inputs
    first_letters = [choice.lower()[0] for choice in choices]
    if len(set(first_letters)) != len(first_letters):
        raise Exception('each choice must have a unique first letter')
    if default is not None and default not in choices:
        raise Exception('default must be in choices')

    # create instructions
    if pre_prompt is None and post_prompt is None:
        pre_prompt = ''
        post_prompt = '\n> '
    elif pre_prompt is None or post_prompt is None:
        raise Exception('must specify both pre_prompt and post_prompt')

    formatted_choices = [
        '(' + choice[0].upper() + ')' + choice[1:].lower() for choice in choices
    ]
    instructions = pre_prompt + ', '.join(formatted_choices) + post_prompt

    if default is not None:
        instructions += default_prefix + str(default)

    # obtain answer
    answer = ''
    while answer not in first_letters:
        answer = input(instructions)

        if default is not None and answer == '':
            answer = default[0]

        answer = answer.lower()

    return first_letters.index(answer)


DirectoryCreateActions = Literal['prompt', 'prompt_and_require', True, False]


class InputDirectoryPathKwargs(TypedDict):
    prompt: str
    default: str | None
    require_absolute: bool
    must_already_exist: bool
    create_directory: DirectoryCreateActions
    add_prompt_symbol: bool
    style: str | None


def input_directory_path(
    prompt: str,
    default: typing.Optional[str] = None,
    require_absolute: bool = True,
    must_already_exist: bool = False,
    create_directory: DirectoryCreateActions = False,
    add_prompt_symbol: bool = True,
    style: typing.Optional[str] = None,
) -> str:

    recursive_kwargs: InputDirectoryPathKwargs = {
        'prompt': prompt,
        'default': default,
        'require_absolute': require_absolute,
        'must_already_exist': must_already_exist,
        'create_directory': create_directory,
        'add_prompt_symbol': add_prompt_symbol,
        'style': style,
    }

    path = input_prompt(prompt=prompt, default=default, style=style)

    # convert path to absolute
    if require_absolute and not os.path.isabs(path):
        abs_path = os.path.abspath(path)
        prompt = 'Full directory path required. Use ' + abs_path + '\n'
        answer = input_yes_or_no(
            prompt=prompt,
            default='yes',
            add_prompt_symbol=add_prompt_symbol,
        )
        if not answer:
            return input_directory_path(**recursive_kwargs)

    # check existence
    if not os.path.isdir(path):
        if must_already_exist:
            print('Path does not exist')
            return input_directory_path(**recursive_kwargs)
        elif create_directory:
            if create_directory == 'prompt':
                answer = input_yes_or_no(prompt='Directory does not exist. Create it? ')
                if answer:
                    os.makedirs(path)
            elif create_directory is True:
                print('Creating directory')
                os.makedirs(path)

    return path
