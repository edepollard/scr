# scr - Screen Session Manager

A screen helper script to manage GNU screen sessions with a default set of named sessions that are always offered, whether active or not.

This is obviously heavily over engineered. Much of what is in here is me trying out things I feel I haven't internalized and the best way to do that for me is to use those things in a meaningful way. This repo is one of my training grounds for internalizing concepts.

## Overview

`scr` provides an interactive menu interface for managing screen sessions, making it easy to:
- Create new screen sessions
- Attach to existing sessions
- Manage a predefined set of session names

## Features

- **Interactive Menu**: Color-coded menu system for easy navigation
- **Default Sessions**: Pre-configured session names (dev, dev2, run, log, test)
- **Session Management**: Automatically detects and displays active screen sessions
- **Configuration**: Customizable via `~/.scr` config file
- **Color Support**: ANSI color output (can be disabled with `--nocolor`)

## Running the Script

Currently, the script must be run using the `run` utility script, which sets up the appropriate Python paths for development mode:

```bash
run scr
```

### Command Line Options

- `-n, --nocolor` - Disable color output
- `-d, --default_sessions` - Comma-separated list of session names

### Examples

```bash
# Run with default settings
run scr

# Disable colors
run scr --nocolor

# Use custom session names
run scr --default_sessions "web,api,db,cache"
```

## Configuration

Create a configuration file at `~/.scr`:

```ini
[scr]
color = True
default_sessions = dev,dev2,run,log,test
```

## Requirements

See [requirements.md](requirements.md) for detailed dependency information.


## Author

Ed Pollard
