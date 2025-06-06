# Markov Databricks MCP

A Model Completion Protocol (MCP) server for Databricks that provides access to Databricks functionality via the MCP protocol. This allows LLM-powered tools to interact with Databricks clusters, jobs, notebooks, and more.

This project is maintained by Olivier Debeuf De Rijcker <olivier@markov.bot>.

Credit for the initial version goes to [@JustTryAI](https://github.com/JustTryAI/databricks-mcp-server).

## Features

- **MCP Protocol Support**: Implements the MCP protocol to allow LLMs to interact with Databricks
- **Databricks API Integration**: Provides access to Databricks REST API functionality
- **Tool Registration**: Exposes Databricks functionality as MCP tools
- **Async Support**: Built with asyncio for efficient operation

## Available Tools

The Databricks MCP Server exposes the following tools:

- **list_clusters**: List all Databricks clusters
- **create_cluster**: Create a new Databricks cluster
- **terminate_cluster**: Terminate a Databricks cluster
- **get_cluster**: Get information about a specific Databricks cluster
- **start_cluster**: Start a terminated Databricks cluster
- **list_jobs**: List all Databricks jobs
- **run_job**: Run a Databricks job
- **list_notebooks**: List notebooks in a workspace directory
- **export_notebook**: Export a notebook from the workspace
- **list_files**: List files and directories in a DBFS path
- **execute_sql**: Execute a SQL statement

## Installation

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended for MCP servers)

### Setup

1. Install `uv` if you don't have it already:

   ```bash
   # MacOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (in PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   ```

   Restart your terminal after installation.

2. Clone the repository:
   ```bash
   git clone https://github.com/markov-kernel/databricks-mcp.git
   cd databricks-mcp
   ```

3. Set up the project with `uv`:
   ```bash
   # Create and activate virtual environment
   uv venv
   
   # On Windows
   .\.venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies in development mode
   uv pip install -e .
   
   # Install development dependencies
   uv pip install -e ".[dev]"
   ```

4. Set up environment variables:
   ```bash
   # Windows
   set DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   set DATABRICKS_TOKEN=your-personal-access-token
   
   # Linux/Mac
   export DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   export DATABRICKS_TOKEN=your-personal-access-token
   ```

   You can also create an `.env` file based on the `.env.example` template.

## Running the MCP Server

### Standalone

To start the MCP server directly for testing or development, run:

```bash
# Activate your virtual environment if not already active
source .venv/bin/activate 

# Run the start script (handles finding env vars from .env if needed)
./scripts/start_mcp_server.sh
```

This is useful for seeing direct output and logs.

### Integrating with VS Code and Copilot

There are two flavours of integration with VS Code and Copilot:
- SSE-based
- stdio-based

#### SSE-based

1. Run the script `./scripts/start_mcp_server_sse.sh` to start the server
1. `ctrl+shift+p` and select MCP: Add Server
1. Select HTTP
1. For URL enter `http://localhost:8000/sse`
1. For name enter `databricks-mcp`
1. Select User Settings if you want to run this in all your VS Code contexts.  Select workspace
if you want to only run it in the context of the current VS Code workspace

/Users/travisdent/Projects/2.Hobby/2025_06_databricks_mcp/scripts/start_mcp_server_sse.sh
#### stdio-based

1. `ctrl+shift+p` and select MCP: Add Server
1. Select Command (stdio)
1. For Command to run enter the full path to the file `start_mcp_server_stdio.sh` (it'll be something like `/Users/<your name>/../../start_mcp_server_stdio.sh`)
1. For name enter `databricks-mcp`
1. Select User Settings if you want to run this in all your VS Code contexts.  Select workspace
if you want to only run it in the context of the current VS Code workspace


If you selected the workspace context you'll see a file `mcp.json` added to the `.vscode` folder of
the current VS Code workspace.  For User Settings, you can see the added server by selecting `ctrl+shift+p` and select "Preferences: Open User Settings (JSON)".

### Integrating with AI Clients

To use this server with AI clients like Cursor or Claude CLI, you need to register it.

#### Cursor Setup

1.  Open your global MCP configuration file located at `~/.cursor/mcp.json` (create it if it doesn't exist).
2.  Add the following entry within the `mcpServers` object, replacing placeholders with your actual values and ensuring the path to `start_mcp_server.sh` is correct:

    ```json
    {
      "mcpServers": {
        // ... other servers ...
        "databricks-mcp-local": { 
          "command": "/absolute/path/to/your/project/databricks-mcp-server/start_mcp_server.sh",
          "args": [],
          "env": {
            "DATABRICKS_HOST": "https://your-databricks-instance.azuredatabricks.net", 
            "DATABRICKS_TOKEN": "dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "RUNNING_VIA_CURSOR_MCP": "true" 
          }
        }
        // ... other servers ...
      }
    }
    ```

3.  **Important:** Replace `/absolute/path/to/your/project/databricks-mcp-server/` with the actual absolute path to this project directory on your machine.
4.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials.
5.  Save the file and **restart Cursor**.

6.  You can now invoke tools using `databricks-mcp-local:<tool_name>` (e.g., `databricks-mcp-local:list_jobs`).

#### Claude CLI Setup

1.  Use the `claude mcp add` command to register the server. Provide your credentials using the `-e` flag for environment variables and point the command to the `start_mcp_server.sh` script using `--` followed by the absolute path:

    ```bash
    claude mcp add databricks-mcp-local \
      -s user \
      -e DATABRICKS_HOST="https://your-databricks-instance.azuredatabricks.net" \
      -e DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
      -- /absolute/path/to/your/project/databricks-mcp-server/start_mcp_server.sh
    ```

2.  **Important:** Replace `/absolute/path/to/your/project/databricks-mcp-server/` with the actual absolute path to this project directory on your machine.
3.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials.

4.  You can now invoke tools using `databricks-mcp-local:<tool_name>` in your Claude interactions.

## Querying Databricks Resources

The repository includes utility scripts to quickly view Databricks resources:

```bash
# View all clusters
uv run scripts/show_clusters.py

# View all notebooks
uv run scripts/show_notebooks.py
```

## Project Structure

```
databricks-mcp-server/
├── src/                             # Source code
│   ├── __init__.py                  # Makes src a package
│   ├── __main__.py                  # Main entry point for the package
│   ├── main.py                      # Entry point for the MCP server
│   ├── api/                         # Databricks API clients
│   ├── core/                        # Core functionality
│   ├── server/                      # Server implementation
│   │   ├── databricks_mcp_server.py # Main MCP server
│   │   └── app.py                   # FastAPI app for tests
│   └── cli/                         # Command-line interface
├── tests/                           # Test directory
├── scripts/                         # Helper scripts
│   ├── start_mcp_server.ps1         # Server startup script (Windows)
│   ├── run_tests.ps1                # Test runner script
│   ├── show_clusters.py             # Script to show clusters
│   └── show_notebooks.py            # Script to show notebooks
├── examples/                        # Example usage
├── docs/                            # Documentation
└── pyproject.toml                   # Project configuration
```

See `project_structure.md` for a more detailed view of the project structure.

## Development

### Code Standards

- Python code follows PEP 8 style guide with a maximum line length of 100 characters
- Use 4 spaces for indentation (no tabs)
- Use double quotes for strings
- All classes, methods, and functions should have Google-style docstrings
- Type hints are required for all code except tests

### Linting

The project uses the following linting tools:

```bash
# Run all linters
uv run pylint src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
```

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests with our convenient script
.\scripts\run_tests.ps1

# Run with coverage report
.\scripts\run_tests.ps1 -Coverage

# Run specific tests with verbose output
.\scripts\run_tests.ps1 -Verbose -Coverage tests/test_clusters.py
```

You can also run the tests directly with pytest:

```bash
# Run all tests
uv run pytest tests/

# Run with coverage report
uv run pytest --cov=src tests/ --cov-report=term-missing
```

A minimum code coverage of 80% is the goal for the project.

## Documentation

- API documentation is generated using Sphinx and can be found in the `docs/api` directory
- All code includes Google-style docstrings
- See the `examples/` directory for usage examples

## Examples

Check the `examples/` directory for usage examples. To run examples:

```bash
# Run example scripts with uv
uv run examples/direct_usage.py
uv run examples/mcp_client_usage.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Ensure your code follows the project's coding standards
2. Add tests for any new functionality
3. Update documentation as necessary
4. Verify all tests pass before submitting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About

 A Model Completion Protocol (MCP) server for interacting with Databricks services. Maintained by markov.bot. 