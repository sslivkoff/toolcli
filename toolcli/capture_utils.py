from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import rich.console


def get_minimal_html_format() -> str:
    return """<pre class="terminal" style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>"""


def save_console_output(
    console: rich.console.Console,
    path: str,
    code_format: str | None = None,
    inline_styles: bool = True,
) -> None:

    if path.endswith('.html'):
        if code_format == 'minimal':
            code_format = get_minimal_html_format()

        console.save_html(
            path,
            inline_styles=inline_styles,
            code_format=code_format,  # type: ignore
        )
    elif path.endswith('.svg'):
        console.save_svg(path, code_format=code_format)  # type: ignore
    else:
        raise Exception('unknown file extension: ' + str(path))
