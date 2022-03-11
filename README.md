# toolcli

`toolcli` makes it simple to create modular command line interfaces

the main usecase for `toolcli` is allowing many cli subcommands to be defined across many files in a performant way


## Features
- lazy loading of files for fast startup times
- is agnostic to synchronous functions or `async` functions
- uses `rich` for colorized help output
- uses `argparse` under the hood for parsing arguments
- no user-facing objects, just simple functions
- built-in support for common subcommands like `help`, `cd`, and `version`
- can use middleware before and/or after main command execution (e.g. for logging or additional context injection)

