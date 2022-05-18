from __future__ import annotations

import os
import importlib

from toolcli import spec


def filetree_to_command_index(
    root_module_name: str,
    postfix: str = '_command.py',
) -> spec.CommandIndex:

    import inspect

    if not postfix.endswith('.py'):
        raise Exception('postfix must end with ".py"')

    command_sequences: list[spec.CommandSequence] = []
    modules = []

    # add root node if it has a get_command_spec attribute
    root_module = importlib.import_module(root_module_name)
    if hasattr(root_module, 'get_command_spec'):
        command_sequences.append(tuple())
        modules.append(root_module_name)

    root_module_path = os.path.dirname(inspect.getfile(root_module))
    for dirname, subdirs, files in os.walk(root_module_path):
        for file in files:
            if file.endswith(postfix):

                relpath = os.path.relpath(dirname, root_module_path)

                command_name = file[: -len(postfix)]
                as_list = relpath.split(os.path.sep) + [command_name]
                command_sequence = tuple(as_list)

                relmodule = relpath.replace(os.path.sep, '.')
                module_name = file[:-3]
                module_ref = (
                    root_module_name + '.' + relmodule + '.' + module_name
                )

                command_sequences.append(command_sequence)
                modules.append(module_ref)

    command_index: spec.CommandIndex = dict(zip(command_sequences, modules))

    return command_index


def add_command_sequence_aliases(
    command_index: spec.CommandIndex,
    config: spec.CLIConfig,
) -> spec.CommandIndex:
    """add command sequence aliases to command index"""
    command_sequence_aliases = config.get('command_sequence_aliases')
    if command_sequence_aliases is not None:

        # add aliases to command index
        command_index = dict(command_index)
        for sequence, spec_ref in command_index.items():
            for alias in command_sequence_aliases:
                if sequence[: len(alias)] == alias:
                    len_alias = len(alias)
                    alias_command = alias + sequence[len_alias:]
                    if alias_command not in command_index:
                        command_index[alias_command] = command_index[sequence]

    return command_index

