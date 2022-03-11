
## File Layout
- `toolcli` allows commands and subcommands to be defined across multiple files to allow for better code organization, modularization, and loading times
- `toolcli.parse_filesystem_commands()` can be used to auto-generate a command index
- example:
    - the following directory structure
        ```
        some_package/
            some_module/
                __init__.py
                s1/
                    a_command.py
                    b_command.py
                s2/
                    c_command.py
                    d_command.py
        ```
    - with the command
        `toolcli.parse_filesystem_commands('some_package.some_module')`
    - would create the following command_index
        ```python
        {
            (): 'some_module',
            ('s1', 'a'): 'some_module.a_command',
            ('s1', 'b'): 'some_module.b_command',
            ('s2', 'c'): 'some_module.c_command',
            ('s2', 'd'): 'some_module.d_command',
        }
        ```
- each module in the command index should define a `get_command_spec()` function
    - the `()` is only added if `some_package.some_module.__init__.py` contains a `get_command_spec()`

## Example Usage

#### Run with filesystem hierarchy commmand definitions
```python
import toolcli


config = {}
command_index = toolcli.parse_filesystem_commands('some_package.some_module')
toolcli.execute_command('<raw command text>', command_index=command_index, config=config)
```

