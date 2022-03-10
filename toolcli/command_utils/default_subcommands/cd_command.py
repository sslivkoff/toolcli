
def get_command_spec():
    return {
        'f': cd_command,
        'args': [
            {'name': 'dirname'},
        ],
        'special': {'cd': True, 'include_parse_spec': True},
        'help': 'change working directory to specified location',
    }


def cd_command(dirname, new_dir_tempfile, parse_spec):

    # get path
    getter = parse_spec['config'].get('cd_dir_getter')
    if getter is None:
        raise Exception('must specify path getter')
    path = getter(dirname)

    # change pwd to path
    with open(new_dir_tempfile, 'w') as f:
        f.write(path)

