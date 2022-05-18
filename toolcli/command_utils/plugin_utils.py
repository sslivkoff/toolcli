from __future__ import annotations

from toolcli import spec


def add_plugin(
    command_index: spec.CommandIndex,
    config: spec.CLIConfig,
    plugin: spec.Plugin,
) -> None:
    """modifies command_index and config in-place"""

    # add to command index
    added_subcommands = []
    plugin_command_index = plugin.get('command_index')
    if plugin_command_index is not None:
        for (
            command_sequence,
            command_spec_reference,
        ) in plugin_command_index.items():
            if command_sequence not in command_index:
                command_index[command_sequence] = command_spec_reference
                added_subcommands.append(command_sequence)

    # add help category
    help_category = plugin.get('help_category')
    if help_category is not None:
        help_subcommand_categories = config.get('help_subcommand_categories')
        if help_subcommand_categories is not None:
            for command_sequence in added_subcommands:
                help_subcommand_categories[command_sequence] = help_category

    # ensure that extra data is present
    required_extra_data = plugin.get('required_extra_data')
    if required_extra_data is not None:
        extra_data = config.get('extra_data')
        if extra_data is None:
            extra_data = {}
        extra_data_getters = config.get('extra_data_getters')
        if extra_data_getters is None:
            extra_data_getters = {}
        for key in required_extra_data:
            if key not in extra_data and key not in extra_data_getters:
                raise Exception('extra_data required: ' + str(key))
