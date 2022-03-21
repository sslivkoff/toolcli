import toolcli

command_index = {
    ('annotate',): 'toolcli.command_utils.dev_subcommands.annotate_command',
}

toolcli.run_cli(
    command_index=command_index,
)

