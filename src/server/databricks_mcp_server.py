"""
Databricks MCP Server

This module implements a standalone MCP server that provides tools for interacting
with Databricks APIs. It follows the Model Context Protocol standard, communicating
via stdio and directly connecting to Databricks when tools are invoked.
"""

import argparse
import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional, Union, cast

from mcp.server import FastMCP
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

from src.api import clusters, dbfs, jobs, notebooks, sql
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    filename="databricks_mcp.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabricksMCPServer(FastMCP):
    """An MCP server for Databricks APIs."""

    def __init__(self):
        """Initialize the Databricks MCP server."""
        super().__init__(
            name="databricks-mcp",
            version="1.0.0",
            instructions="Use this server to manage Databricks resources",
        )
        logger.info("Initializing Databricks MCP server")
        logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all Databricks MCP tools."""

        # Cluster management tools
        @self.tool(
            name="list_clusters",
            description="List all Databricks clusters",
        )
        async def list_clusters(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing clusters with params: {params}")
            try:
                result = await clusters.list_clusters()
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing clusters: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster with parameters: cluster_name (required), spark_version (required), node_type_id (required), num_workers, autotermination_minutes",
        )
        async def create_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Creating cluster with params: {params}")
            try:
                result = await clusters.create_cluster(params)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="terminate_cluster",
            description="Terminate a Databricks cluster with parameter: cluster_id (required)",
        )
        async def terminate_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Terminating cluster with params: {params}")
            try:
                result = await clusters.terminate_cluster(params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error terminating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="get_cluster",
            description="Get information about a specific Databricks cluster with parameter: cluster_id (required)",
        )
        async def get_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting cluster info with params: {params}")
            try:
                result = await clusters.get_cluster(params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting cluster info: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="start_cluster",
            description="Start a terminated Databricks cluster with parameter: cluster_id (required)",
        )
        async def start_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Starting cluster with params: {params}")
            try:
                result = await clusters.start_cluster(params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error starting cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Job management tools
        @self.tool(
            name="list_jobs",
            description="List all Databricks jobs",
        )
        async def list_jobs(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing jobs with params: {params}")
            try:
                result = await jobs.list_jobs()
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing jobs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Job management tools
        @self.tool(
            name="list_job_runs",
            description="List the latest failed runs of all Databricks jobs with parameters:  job_id (optional, filter by specific job)",
        )
        async def list_job_runs(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing job runs with params: {params}")
            try:
                job_id = params.get("job_id")
                if job_id is None:
                    logger.info("No job_id provided, listing runs for all jobs")
                    result = await jobs.list_job_runs()
                else:
                    result = await jobs.list_job_runs(params.get("job_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing job runs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="get_job_run_details",
            description="Get details of a specific job run with parameter: run_id (required)",
        )
        async def get_job_run_details(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting details of job run with params: {params}")
            try:
                run_id = params.get("run_id")
                if not run_id:
                    raise ValueError("run_id is required")
                result = await jobs.get_job_run_details(run_id)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting details of job run: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="get_task_run_output",
            description="Get the output of a specific task run with parameters: run_id (required)",
        )
        async def get_task_run_output(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting task run output with params: {params}")
            try:
                run_id = params.get("run_id")
                if not run_id:
                    raise ValueError("run_id is required")

                result = await jobs.get_task_run_output(run_id)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting task run output: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="run_job",
            description="Run a Databricks job with parameters: job_id (required), notebook_params (optional)",
        )
        async def run_job(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Running job with params: {params}")
            try:
                notebook_params = params.get("notebook_params", {})
                result = await jobs.run_job(params.get("job_id"), notebook_params)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error running job: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Notebook management tools
        @self.tool(
            name="list_notebooks",
            description="List notebooks in a workspace directory with parameter: path (required)",
        )
        async def list_notebooks(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing notebooks with params: {params}")
            try:
                result = await notebooks.list_notebooks(params.get("path"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing notebooks: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="export_notebook",
            description="Export a notebook from the workspace with parameters: path (required), format (optional, one of: SOURCE, HTML, JUPYTER, DBC)",
        )
        async def export_notebook(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Exporting notebook with params: {params}")
            try:
                format_type = params.get("format", "SOURCE")
                result = await notebooks.export_notebook(params.get("path"), format_type)

                # For notebooks, we might want to trim the response for readability
                content = result.get("content", "")
                if len(content) > 1000:
                    summary = f"{content[:1000]}... [content truncated, total length: {len(content)} characters]"
                    result["content"] = summary

                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error exporting notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # DBFS tools
        @self.tool(
            name="list_files",
            description="List files and directories in a DBFS path with parameter: dbfs_path (required)",
        )
        async def list_files(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing files with params: {params}")
            try:
                result = await dbfs.list_files(params.get("dbfs_path"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing files: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # SQL tools
        @self.tool(
            name="execute_sql",
            description="Execute a SQL statement with parameters: statement (required), warehouse_id (required), catalog (optional), schema (optional)",
        )
        async def execute_sql(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Executing SQL with params: {params}")
            try:
                statement = params.get("statement")
                warehouse_id = params.get("warehouse_id")
                catalog = params.get("catalog")
                schema = params.get("schema")

                result = await sql.execute_statement(
                    statement=statement, warehouse_id=warehouse_id, catalog=catalog, schema=schema
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error executing SQL: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]


async def main():
    """Main entry point for the MCP server."""
    # get arguments from command line using argparse
    parser = argparse.ArgumentParser(description="Databricks MCP Server")
    # add argument for server type, default to stdio
    parser.add_argument(
        "--server-type",
        choices=["stdio", "sse"],
        default="stdio",
        help="Type of server to run (stdio or sse)",
    )
    args = parser.parse_args()

    try:
        logger.info("Starting Databricks MCP server")
        server = DatabricksMCPServer()

        if args.server_type == "stdio":
            logger.info("Running server in stdio mode")
            # Run the server using stdio
            await server.run_stdio_async()
        elif args.server_type == "sse":
            logger.info("Running server in SSE mode")
            # Run the server using Server-Sent Events (SSE)
            await server.run_sse_async()

    except Exception as e:
        logger.error(f"Error in Databricks MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Turn off buffering in stdout
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    asyncio.run(main())
