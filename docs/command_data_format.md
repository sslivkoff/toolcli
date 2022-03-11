
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

