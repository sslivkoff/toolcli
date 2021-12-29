import os
import typing
import sys


InvalidAction = typing.Literal['retry', 'exit']


class _InputYesNoKwargs(typing.TypedDict):
    prompt: str
    invalid_action: InvalidAction
    default: typing.Optional[str]
    default_prefix: typing.Optional[str]
    default_postfix: typing.Optional[str]
    add_prompt_symbol: bool


def input_prompt(
    prompt: str = '',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
) -> str:

    # add default prompt
    if default is not None:
        if default_prefix is None:
            default_prefix = '\n(default = '
        if default_postfix is None:
            default_postfix = ')\n'
        prompt += default_prefix + str(default) + default_postfix
    if prompt.endswith('\n') and add_prompt_symbol:
        prompt += '> '

    # obtain response
    try:
        response = input(prompt)
    except KeyboardInterrupt:
        print()
        sys.exit()

    # set default response
    if default is not None and response == '':
        response = default

    return response


def input_yes_or_no(
    prompt: str = '',
    invalid_action: InvalidAction = 'exit',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
) -> bool:

    recursive_kwargs: _InputYesNoKwargs = {
        'prompt': prompt,
        'invalid_action': invalid_action,
        'default': default,
        'default_prefix': default_prefix,
        'default_postfix': default_postfix,
        'add_prompt_symbol': add_prompt_symbol,
    }

    response = input_prompt(
        prompt=prompt,
        default=default,
        default_prefix=default_prefix,
        default_postfix=default_postfix,
        add_prompt_symbol=add_prompt_symbol,
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
    invalid_action: InvalidAction = 'exit',
    default: typing.Optional[str] = None,
    default_prefix: typing.Optional[str] = None,
    default_postfix: typing.Optional[str] = None,
    add_prompt_symbol: bool = True,
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
        full_prompt += '    ' + str(c + 1) + '. ' + choice + '\n'

    # select input
    choice = input_prompt(
        prompt=full_prompt,
        default=default,
        default_prefix=default_prefix,
        default_postfix=default_postfix,
        add_prompt_symbol=add_prompt_symbol,
    )

    try:

        # return valid input

        return int(choice) - 1

    except (ValueError, IndexError):

        # handle invalid input

        if invalid_action == 'exit':
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
            )

        else:
            raise Exception('unknown invalid_action: ' + str(invalid_action))


def input_first_letter_choice(
    choices: list[str],
    pre_prompt: typing.Optional[str] = None,
    post_prompt: typing.Optional[str] = None,
    default: typing.Optional[str] = None,
    default_prefix: str = '\n\ndefault = ',
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


DirectoryCreateActions = typing.Literal['prompt', 'prompt_and_require', True]


class InputFilenameOrDirectoryKwargs(typing.TypedDict, total=False):
    prompt: str
    default_directory: typing.Optional[str]
    default_filename: typing.Optional[str]
    create_directory: DirectoryCreateActions
    confirm_filename: bool
    add_prompt_symbol: bool


def input_filename_or_directory(
    prompt: str,
    default_directory: typing.Optional[str] = None,
    default_filename: typing.Optional[str] = None,
    create_directory: DirectoryCreateActions = 'prompt',
    confirm_filename: bool = True,
    add_prompt_symbol: bool = True,
):

    recursive_kwargs: InputFilenameOrDirectoryKwargs = {
        'prompt': prompt,
        'default_directory': default_directory,
        'default_filename': default_filename,
        'create_directory': create_directory,
        'confirm_filename': confirm_filename,
        'add_prompt_symbol': add_prompt_symbol,
    }

    path = input_prompt(prompt=prompt, default=default_directory)
    if path == '':
        return input_filename_or_directory(**recursive_kwargs)
    path = os.path.abspath(os.path.normpath(os.path.expanduser(path)))

    # assume path is a directory if does not have a file extension
    is_directory = os.path.splitext(path)[-1] == ''

    # add filename if is a directory and default filename given
    if is_directory and default_filename is not None:
        path = os.path.join(path, default_filename)
        print('This is a directory. Will use', path)
        if confirm_filename:
            if not input_yes_or_no(
                'Continue? ',
                default='yes',
                default_prefix='(default = ',
            ):
                print()
                return input_filename_or_directory(**recursive_kwargs)

    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        if create_directory in ['prompt', 'prompt_and_require']:
            directory_prompt = 'Directory does not exist. Create directory? '
            if input_yes_or_no(
                prompt=directory_prompt,
                default='yes',
                default_prefix='(default = ',
            ):
                print()
                print('Creating', directory)
                os.makedirs(directory)
            elif create_directory == 'prompt_and_require':
                print('Directory must exist')
                print()
                return input_filename_or_directory(**recursive_kwargs)

        elif create_directory is True:
            print('Creating', directory)
            os.makedirs(directory)

    return path


# def input_confirm(
#     value: typing.Any,
#     pre_prompt: typing.Optional[str] = None,
#     post_prompt: typing.Optional[str] = None,
#     alternative_str: typing.Optional[str] = None,
#     # jsonify: bool = False,
# ):

#     # initialize args
#     if pre_prompt is None and post_prompt is None:
#         pre_prompt = 'use '
#         post_prompt = '? '
#     elif pre_prompt is None or post_prompt is None:
#         raise Exception('must specify both pre_prompt and post_prompt')
#     if alternative_str is None:
#         alternative_str = 'what to use instead?\n'

#     # assemble prompt
#     prompt = pre_prompt + str(value) + post_prompt

#     # confirm value
#     answer = input_yes_or_no(prompt=prompt, invalid_action='retry')
#     if answer:
#         return value
#     else:

#         # obtain new answer
#         new_answer = input(alternative_str)

#         # # jsonify new answer
#         # if jsonify:
#         #     new_answer = json.loads(new_answer)

#         # confirm new value
#         return input_confirm(
#             value=new_answer,
#             pre_prompt=pre_prompt,
#             post_prompt=post_prompt,
#             alternative_str=alternative_str,
#             # jsonify=jsonify,
#         )

