from __future__ import annotations

import os
import typing
import types

if typing.TYPE_CHECKING:
    import rich.console

from toolcli import spec
from toolcli.command_utils import output_utils
from toolcli.command_utils.parsing import command_parsing


def print_prefix_help(
    command_sequence: spec.CommandSequence,
    parse_spec: spec.ParseSpec,
    console: rich.console.Console | None = None,
) -> None:
    if console is None:
        console = output_utils.get_rich_console(parse_spec=parse_spec)

    config = parse_spec['config']
    command_index = parse_spec['command_index']

    console.print(
        '[title]usage:[/title]\n    '
        + '[option]'
        + config['base_command']
        + ' '
        + ' '.join(command_sequence)
        + ' <subcommand> \[options][/option]'
    )
    console.print()
    console.print(
        '[title]description:[/title]\n'
        + '    [option]'
        + config['base_command']
        + ' '
        + ' '.join(command_sequence)
        + '[/option] [description]is used to call subcommands[/description]\n\n'
        + '    [description]to view help about a specific subcommand run:\n'
        + '        [option]'
        + config['base_command']
        + ' '
        + ' '.join(command_sequence)
        + ' <subcommand> -h[/option][/description]'
    )

    if command_index is None:
        return

    console.print()
    console.print('[title]available subcommands:[/title]')

    chop = len(command_sequence)
    subsequences: list[str] = []
    helps: list[str] = []
    for other_command_sequence, command_spec_reference in command_index.items():
        if other_command_sequence[:chop] == command_sequence:
            subsequences.append(' '.join(other_command_sequence[chop:]))
            command_spec = command_parsing.resolve_command_spec(
                command_spec_reference
            )
            help = command_spec.get('help', '')
            if isinstance(help, str):
                helps.append(help)
            elif isinstance(help, types.FunctionType):
                helps.append(help())
            else:
                raise Exception('unknown help format')

    longest_subcommand = max(len(item) for item in subsequences)
    for subsequence, help in zip(subsequences, helps):
        text = (
            '    [option]'
            + subsequence.ljust(longest_subcommand)
            + '[/option]    [description]'
            + help
            + '[/description]'
        )
        console.print(text)


def get_help_dir_hash_path(
    command_index: spec.CommandIndex, help_cache_dir: str
) -> str:
    import hashlib

    command_index_str = str(sorted(command_index.items()))
    name_hash = hashlib.md5(command_index_str.encode()).hexdigest()
    help_cache_path = os.path.join(help_cache_dir, name_hash)
    return help_cache_path


def print_help_from_cache(
    command_index: spec.CommandIndex, help_cache_dir: str
) -> bool:
    help_cache_path = get_help_dir_hash_path(command_index, help_cache_dir)
    if os.path.isfile(help_cache_path):
        with open(help_cache_path, 'r') as f:
            contents = f.read()
        print(contents, end='')
        return True
    else:
        return False


def save_help_text_to_cache(
    help_text: str,
    command_index: spec.CommandIndex,
    help_cache_dir: str,
) -> None:
    help_cache_path = get_help_dir_hash_path(command_index, help_cache_dir)
    with open(help_cache_path, 'w') as f:
        f.write(help_text)


def print_root_command_help(
    parse_spec: spec.ParseSpec,
    console: rich.console.Console | None = None,
    include_links: bool = False,
    only_category: str | None = None,
    show_hidden: bool = False,
    help_cache_dir: str | None = None,
) -> None:
    """print help message for a root command"""

    config = parse_spec['config']
    command_index = parse_spec['command_index']
    base_command = config.get('base_command', '<base-command>')

    # check cache and use it if possible
    if help_cache_dir is None:
        help_cache_dir = config.get('help_cache_dir')
    if help_cache_dir is not None:
        command_index = parse_spec.get('command_index')
        if command_index is not None:
            printed = print_help_from_cache(
                command_index=command_index,
                help_cache_dir=help_cache_dir,
            )
            if printed:
                return

    # create console
    if help_cache_dir is not None:
        old_console = console

        import io

        file = io.StringIO()

        console = output_utils.get_rich_console(
            parse_spec=parse_spec,
            file=file,
        )
    else:
        if console is None:
            console = output_utils.get_rich_console(parse_spec=parse_spec)

    # print usage and description
    console.print(
        '[title]usage:[/title]\n    '
        + '[option]'
        + base_command
        + ' <subcommand> \[options][/option]'
    )
    console.print()
    console.print('[title]description:[/title]')
    if config.get('description') is not None:
        lines = ['    ' + line for line in config['description'].split('\n')]
        console.print('[description]' + '\n'.join(lines) + '[/description]')
        console.print()
    console.print(
        '    [description]to view help about a specific subcommand run:\n'
        + '        [option]'
        + base_command
        + ' <subcommand> -h[/option][/description]'
    )

    # print subcommands
    if command_index is not None:

        # gather command_spec and help text of each subcommand
        subcommands = {}
        command_specs = {}
        helps = {}
        for command_sequence, command_spec_spec in command_index.items():
            try:
                command_spec = command_parsing.resolve_command_spec(
                    command_spec_spec
                )
            except Exception:
                command_spec = {}
            command_specs[command_sequence] = command_spec

            subcommands[command_sequence] = ' '.join(command_sequence)
            subcommand_help = command_spec.get('help', '')
            if isinstance(subcommand_help, str):
                help_str = subcommand_help
            elif isinstance(subcommand_help, types.FunctionType):
                help_str = subcommand_help(parse_spec=parse_spec)
            else:
                help_str = ''
            help_str = help_str.split('\n')[0]
            helps[command_sequence] = help_str

        # print subcommand header
        console.print()
        if only_category is not None:
            subcommand_header = only_category + ' subcommands:'
        else:
            subcommand_header = 'available subcommands:'
        console.print('[title]' + subcommand_header + '[/title]')

        # get help_url_getter function
        if include_links:
            help_url_getter = config.get('help_url_getter')
        else:
            help_url_getter = None

        # get category of each subcommand
        help_subcommand_categories = config.get('help_subcommand_categories')
        if help_subcommand_categories is not None:
            is_capital = next(
                iter(help_subcommand_categories.values())
            ).isupper()
            if is_capital:
                other = 'Other'
            else:
                other = 'other'
            subcommands_by_category: typing.MutableMapping[
                str, list[spec.CommandSequence]
            ] = {}
            for command_sequence in sorted(command_index.keys()):
                category = help_subcommand_categories.get(
                    command_sequence, other
                )
                subcommands_by_category.setdefault(category, [])
                subcommands_by_category[category].append(command_sequence)
        else:
            subcommands_by_category = {'Other': list(command_index.keys())}
        print_subcommand_categories = (
            len(subcommands_by_category) > 1 and only_category is None
        )

        # print commands of each category
        max_len_subcommand = max(
            len(subcommand) for subcommand in subcommands.values()
        )
        category_order = sorted(subcommands_by_category.keys())
        for other in ['other', 'Other']:
            if other in category_order:
                category_order.pop(category_order.index(other))
                category_order.append(other)

        for category in category_order:
            command_sequences = subcommands_by_category[category]

            if only_category and category != only_category:
                continue

            if print_subcommand_categories:
                console.print()
                console.print('    [title]' + category + ' subcommands[/title]')

            for command_sequence in command_sequences:
                if len(command_sequence) == 0:
                    continue
                if not show_hidden and command_specs[command_sequence].get(
                    'hidden'
                ):
                    continue

                # get url of command
                if help_url_getter is not None:
                    try:
                        url = help_url_getter(
                            subcommand=command_sequence,
                            parse_spec=parse_spec,
                        )
                    except Exception:
                        url = None
                else:
                    url = None

                # create text
                text = (
                    '    [option]'
                    + subcommands[command_sequence].ljust(max_len_subcommand)
                    + '[/option]    [description]'
                    + helps[command_sequence]
                    + '[/description]'
                )

                # print text
                if url is None:
                    console.print(text)
                else:
                    console.print(text, style='link ' + url)

    if help_cache_dir is not None:
        file.seek(0)
        help_text = file.read()
        if old_console is None:
            old_console = output_utils.get_rich_console(parse_spec=parse_spec)
        print(help_text, end='')
        if command_index is not None:
            save_help_text_to_cache(help_text, command_index, help_cache_dir)
