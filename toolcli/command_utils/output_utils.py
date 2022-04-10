def get_rich_console(parse_spec, record=False):

    import rich.console
    import rich.theme

    style_theme = parse_spec['config'].get('style_theme')
    if style_theme is None:
        style_theme = {}
    console = rich.console.Console(
        theme=rich.theme.Theme(style_theme, inherit=False),  # type: ignore
        record=record,
    )

    return console

