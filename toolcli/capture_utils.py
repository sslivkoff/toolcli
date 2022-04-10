def get_minimal_html_format():
    return """<pre class="terminal" style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>"""


def save_console_output(console, path, code_format=None, inline_styles=True):

    if path.endswith('.html'):
        if code_format == 'minimal':
            code_format = get_minimal_html_format()

        console.save_html(
            path,
            inline_styles=inline_styles,
            code_format=code_format,
        )
    elif path.endswith('.svg'):
        console.save_svg(path, code_format=code_format)
    else:
        raise Exception('unknown file extension: ' + str(path))

