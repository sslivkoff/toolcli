from __future__ import annotations

import toolcli
from toolcli.command_utils import help_utils


def get_cd_help(parse_spec: toolcli.ParseSpec) -> str:
    program_name = parse_spec.get('config', {}).get('base_command', 'PROGRAM')
    return 'change working directory to ' + program_name + '-related location'


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': cd_command,
        'help': get_cd_help,
        'args': [
            {'name': 'dirname', 'help': 'name of directory'},
        ],
        'extra_data': ['cd_destination_tempfile', 'parse_spec'],
    }


cd_snippet_template = """function {program_name} {
    local tempfile="$(mktemp -t tmp.XXXXXX)"
    command {program_name} "$@" --cd-destination-tempfile "$tempfile"
    if [[ -s "$tempfile" ]]; then
        cd "$(realpath $(cat "$tempfile"))"
    fi
    rm -f "$tempfile" 2>/dev/null
}"""


def cd_command(
    dirname: str,
    cd_destination_tempfile: str,
    parse_spec: toolcli.ParseSpec,
) -> None:

    if cd_destination_tempfile is None:
        print('using the cd subcommand requires special configuration')
        print()
        print(
            'add the following snippet to your shell config (e.g. ~/.profile):'
        )
        default_name = '<PROGRAM_NAME>'
        program_name = parse_spec.get('config', {}).get(
            'base_command', default_name
        )
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
    try:
        path = getter(dirname)
    except Exception:
        print('could not find path')
        print()
        help_utils.print_cd_dirs(parse_spec=parse_spec)
        return

    # change pwd to path
    with open(cd_destination_tempfile, 'w') as f:
        f.write(path)
