from .. import parsing


def print_subcommand_usage(parse_spec):
    config = parse_spec['config']
    command_sequence = parse_spec['command_sequence']
    command_spec = parse_spec['command_spec']

    required_args = []
    for arg_spec in command_spec.get('args', []):
        name = arg_spec['name']
        if isinstance(name, str) and not name.startswith('-'):
            required_args.append('<' + name + '>')
        elif arg_spec.get('required'):
            if isinstance(name, str):
                flag = name
            else:
                for subname in name:
                    if subname.startswith('--'):
                        flag = subname
                        break
                else:
                    flag = name[0]
            required_args.append(
                flag + ' <' + parsing.get_arg_name(arg_spec) + '>'
            )

    usage_str = (
        config['base_command']
        + ' '
        + ' '.join(command_sequence)
        + ' '
        + ' '.join(required_args)
    )
    usage_str += ' [options]'

    print('usage:', usage_str)


def print_subcommand_help(parse_spec):
    command_spec = parse_spec['command_spec']

    print_subcommand_usage(parse_spec)

    # print description
    if 'help' in command_spec:
        print()
        print(command_spec['help'])

    # print arg info
    arg_names = []
    arg_helps = []
    for arg_spec in command_spec['args']:
        if arg_spec.get('internal'):
            continue
        name = arg_spec['name']
        if isinstance(name, str) and not name.startswith('-'):
            name = '<' + name + '>'
        arg_names.append(name)
        arg_helps.append(arg_spec.get('help', ''))
    max_name_len = max(len(name) for name in arg_names)
    arg_names = [name.rjust(max_name_len) for name in arg_names]
    print()
    print('arguments:')
    print()
    for a in range(len(arg_names)):
        print('    ' + arg_names[a] + '    ' + arg_helps[a])

