"""
API for managing Databricks jobs.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def create_job(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Databricks job.

    Args:
        job_config: Job configuration

    Returns:
        Response containing the job ID

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Creating new job")
    return make_api_request("POST", "/api/2.2/jobs/create", data=job_config)


async def run_job(job_id: int, notebook_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run a job now.

    Args:
        job_id: ID of the job to run
        notebook_params: Optional parameters for the notebook

    Returns:
        Response containing the run ID

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Running job: {job_id}")

    run_params = {"job_id": job_id}
    if notebook_params:
        run_params["notebook_params"] = notebook_params

    return make_api_request("POST", "/api/2.2/jobs/run-now", data=run_params)


async def list_jobs() -> Dict[str, Any]:
    """
    List all jobs.

    Returns:
        Response containing a list of jobs

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing all jobs")
    return make_api_request("GET", "/api/2.2/jobs/list")


# TODO: Use pagination and date range filters
async def list_job_runs(job_id: Optional[int]) -> Dict[str, Any]:
    """
    List all runs for all jobs.

    Returns:
        Response containing a list of job runs

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing all job runs")
    if job_id is None:
        logger.info("No job ID provided, listing runs for all jobs")
        return make_api_request("GET", "/api/2.2/jobs/runs/list")

    return make_api_request("GET", "/api/2.2/jobs/runs/list", params={"job_id": job_id})


async def get_job_run_details(run_id: int) -> Dict[str, Any]:
    """
    Retrieve details for a specific job run.

    Args:
        run_id: ID of the job run

    Returns:
        Response containing job run details

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Retrieving details for job run: {run_id}")
    return make_api_request("GET", "/api/2.2/jobs/runs/get", params={"run_id": run_id})


# Function to return task run output with input run_id
async def get_task_run_output(run_id: int) -> Dict[str, Any]:
    """
    Get the output of a specific task run.

    Args:
        run_id: ID of the task run

    Returns:
        Response containing the task run output

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting output for task run: {run_id}")
    return make_api_request("GET", "/api/2.2/jobs/runs/get-output", params={"run_id": run_id})


async def get_job(job_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job.

    Args:
        job_id: ID of the job

    Returns:
        Response containing job information

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for job: {job_id}")
    return make_api_request("GET", "/api/2.2/jobs/get", params={"job_id": job_id})


async def update_job(job_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing job.

    Args:
        job_id: ID of the job to update
        new_settings: New job settings

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating job: {job_id}")

    update_data = {"job_id": job_id, "new_settings": new_settings}

    return make_api_request("POST", "/api/2.2/jobs/update", data=update_data)


async def delete_job(job_id: int) -> Dict[str, Any]:
    """
    Delete a job.

    Args:
        job_id: ID of the job to delete

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting job: {job_id}")
    return make_api_request("POST", "/api/2.2/jobs/delete", data={"job_id": job_id})


async def get_run(run_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job run.

    Args:
        run_id: ID of the run

    Returns:
        Response containing run information

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for run: {run_id}")
    return make_api_request("GET", "/api/2.2/jobs/runs/get", params={"run_id": run_id})


async def cancel_run(run_id: int) -> Dict[str, Any]:
    """
    Cancel a job run.

    Args:
        run_id: ID of the run to cancel

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Cancelling run: {run_id}")
    return make_api_request("POST", "/api/2.2/jobs/runs/cancel", data={"run_id": run_id})
