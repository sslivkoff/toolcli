# toolcli

`toolcli` makes it simple to create modular command line interfaces

the main usecase for `toolcli` is allowing cli subcommands to be defined across many files in a performant way


## Features
- lazy loading of files for fast startup times
- uses `argparse` for parsing individual arguments once the subcommand is determined
- no user-facing objects, just simple functions
- use `include_debug_arg=True` in config to add an automatic debugger to a command when the command fails
- can use middleware before and/or after main command execution (e.g. for logging or additional context injection)
- simple syntax to call one command from within another command


## Contents
- [Example Usage](#Example-Usage)
- [Command Data Format](#Command-Data-Format)
- [Command Execution Sequence](#Command-Execution-Sequence)
- [Configuration Options](#Configuration-Options)


## Example Usage

#### Run with filesystem hierarchy commmand definitions
```python
import toolcli


config = {}
command_index = toolcli.parse_filesystem_commands('some_package.some_module')
toolcli.execute_command('<raw command text>', command_index=command_index, config=config)
```

## Command Data Format

#### Raw Commands
- a **raw command** is a string of user input passed to the program
- a raw command is split into its `command_sequence` and its `command_arguments`

#### Command Sequence
- a **command_sequence** is the tuple of subcommands at the beginning of a raw command
- for example, in the raw command `./scripy.py add buffer --arg1 0 --verbose`, the command sequence is `('add', 'buffer')`

#### Command Spec
- every command sequence has a command spec that instructs how to parse and run a command
- for example if a command is defined by the spec:
```python
command_spec_xyz = {
    'f': some_function,
    'help': 'Help text about command',
    'args': [
        {
            'name': 'arg1',
            'kwargs': {'Text': 'Any'},
            'completer': 'Function',
        },
    ]
}```
- then executing that command will call `some_function(arg1=arg1)` 

#### Command Index
- the **command index** maps each command sequence to a command spe
- a command index is a dict that maps command sequences to locations of command specs:
```python
command_index = {
    ('subcommand1'): 'some_function',
    ('subcommand1', 'subcommand2'): 'some_module',
    ('subcommand3'): 'command_spec',
}
```


## Command Execution Sequence
- starting with a raw command, command execution is similar to the following:
```python
command_sequence = parse_command_sequence(raw_command)
command_spec = resolve_command_spec(command_index[command_sequence])
command_args = parse_command_args(raw_command, command_spec['args'])
_execute_middleware(config['pre_middlewares'], command_args)
f = resolve_command_function(command_spec['f'])
f(**command_args)
_execute_middleware(config['post_middlewares'], command_args)
```


## Configuration Options



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




## Standard Commands and Args

- these are on by default but can be disabled

## Standard Commands
- `('help')` outputs help menu
- `('command_index')` outputs command_index
- `('command_spec')` shows the command spec parsed for a given command

## Standard Arguments
- `'--help'`, `'-h'` help
- `'--debug'` enter debugger if exception raised

## Recommended Commands
- `setup` perform any setup operations (e.g. config initialization)
- `config` print out current config
- `cd` change to relevant directories (e.g. data directories)


## Longer Term Plans
- cli command daemon for faster starup times

