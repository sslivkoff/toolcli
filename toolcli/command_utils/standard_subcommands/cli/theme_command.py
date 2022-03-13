import rich

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': theme_command,
        'help': 'display cli style theme',
        'special': {
            'include_parse_spec': True,
            'hidden': True,
        },
    }


def theme_command(parse_spec):
    config = parse_spec.get('config')
    if config is None:
        print('no theme')
    else:
        theme = config.get('style_theme')
        if theme is None:
            print('no theme')
        else:
            longest = max(len(key) for key in theme.keys())
            longest = longest + 1
            for key, value in theme.items():
                rich.print(
                    (key + ':').ljust(longest)
                    + '  '
                    + '['
                    + value
                    + ']'
                    + value
                    + '[/'
                    + value
                    + ']',
                )

