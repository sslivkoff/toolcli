import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': cd_command,
        'help': 'change working directory to specified location',
        'args': [
            {'name': 'dirname'},
        ],
        'special': {'cd': True, 'include_parse_spec': True},
    }


def cd_command(
    dirname: str,
    new_dir_tempfile: str,
    parse_spec: toolcli.ParseSpec,
) -> None:

    # get path
    getter = parse_spec['config'].get('cd_dir_getter')
    if getter is None:
        raise Exception('must specify path getter')
    path = getter(dirname)

    # change pwd to path
    with open(new_dir_tempfile, 'w') as f:
        f.write(path)

