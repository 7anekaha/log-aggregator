# Log Aggregator

A lightweight real-time log aggregation dashboard built with Python, AsyncIO, and Textual. It streams log messages from configured services into a live terminal UI, lets you filter by keyword or regex, and highlights each service with a custom color.

## Features

- Real-time log ingestion from multiple configured services
- Async queue-based log processing with timestamp ordering
- Textual-based TUI dashboard with a live log panel
- Per-service colored log output
- Regex and substring filtering for log messages, service names, and timestamps
- Active filter chips with quick remove behavior
- Pause/resume logging at runtime
- Keyboard-driven navigation and controls
- YAML-based service configuration
- Support for multiple service types, including random log generation and AWS-style service definitions

## How it works

The application starts in `main.py` and loads the service definitions from `configuration.yaml`.

Each configured service is instantiated as a background async worker. Logs are pushed into a shared priority queue, and a consumer reads them, applies filters, and renders them in the TUI.

## Project structure

- `main.py` — application entry point
- `configuration.yaml` — service definitions
- `definitions/` — log, filter, and config models
- `services/` — service implementations and consumer logic
- `tui/` — Textual interface and filter widgets

## Configuration

The project reads its configuration from `configuration.yaml`.

Example:

```yaml
services:
  - name: Service1
    color: red
    type: random

  - name: Service2
    color: blue
    type: random
```

Supported service types:

- `random` — generates synthetic log messages at a random interval
- `aws` — expects an `arn` value in the config and is validated by the config model

Example AWS-style configuration:

```yaml
services:
  - name: BillingLogs
    color: green
    type: aws
    arn: arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/billing
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install the project and dependencies:

```bash
pip install -e .
```

## Running the app

```bash
python main.py
```

## Keyboard controls

- `f` — focus the filter input
- `r` — focus the filter chips for quick selection
- `p` — pause or resume log generation/consumption
- `q` — quit the application
- `Enter` in the filter box — add a new filter
- `Esc` while focused in the filter input — clear focus
- Left/right arrow keys on a filter chip — move between active filters

## Filtering

Type a keyword or regex into the filter input and press Enter.

Filters are applied to:

- log message text
- service name
- timestamp string

The filter engine supports case-insensitive regex matching, and it falls back to plain substring matching for invalid regex patterns.

## Example usage

1. Start the app.
2. Watch log messages populate in the live TUI.
3. Enter `Service1` or `Log message` in the filter box.
4. Press `p` to pause activity when you need to inspect the output.
5. Remove filters by pressing the chip or using the UI controls.
6. Press `q` to exit cleanly.

## Notes

This project is intended as a real-time log monitoring and filtering utility. It is especially useful for demoing async log pipelines, event-driven consumer patterns, and Textual UI development in Python.
