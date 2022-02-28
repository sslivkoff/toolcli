def get_command_spec():
    return {
        'name': 'version',
        'f': version_command,
        'help': 'print cli version',
        'special': {'parse_spec': True},
    }


def version_command(parse_spec):
    version = parse_spec['config'].get('version')
    if version is None:
        raise Exception('unknown version')
    else:
        print(version)

