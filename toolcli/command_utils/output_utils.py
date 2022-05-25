from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import rich.console

from toolcli import spec


def get_rich_console(
    parse_spec: spec.ParseSpec,
    record: bool = False,
    file: typing.TextIO | None=None,
) -> rich.console.Console:

    import rich.console
    import rich.theme

    style_theme = parse_spec['config'].get('style_theme')
    if style_theme is None:
        style_theme = {}
    console = rich.console.Console(
        theme=rich.theme.Theme(style_theme, inherit=False),  # type: ignore
        record=record,
        file=file,
        color_system='truecolor',
    )

    return console
