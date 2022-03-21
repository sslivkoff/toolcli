from __future__ import annotations

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


cd_snippet_template = """function {program_name} {
    local tempfile="$(mktemp -t tmp.XXXXXX)"
    command {program_name} "$@" --new_dir_tempfile "$tempfile"
    if [[ -s "$tempfile" ]]; then
        cd "$(cat "$tempfile")"
    fi
    rm -f "$tempfile" 2>/dev/null
}"""


def cd_command(
    dirname: str,
    new_dir_tempfile: str,
    parse_spec: toolcli.ParseSpec,
) -> None:

    if new_dir_tempfile is None:
        print('using the cd subcommand requires special configuration')
        print()
        print(
            'add the following snippet to your shell config (e.g. ~/.profile):'
        )
        default_name = '<PROGRAM_NAME>'
        program_name = parse_spec.get('config', {}).get('base_command', default_name)
        cd_snippet = cd_snippet_template.replace('{program_name}', program_name)
        print()
        print(cd_snippet)
        if program_name == default_name:
            print()
            print('where', default_name, 'is the name of the root command')
        return

    # get path
    getter = parse_spec['config'].get('cd_dir_getter')
    if getter is None:
        raise Exception('must specify path getter')
    path = getter(dirname)

    # change pwd to path
    with open(new_dir_tempfile, 'w') as f:
        f.write(path)

