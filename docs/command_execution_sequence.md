
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

