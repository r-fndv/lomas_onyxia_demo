from collections.abc import AsyncGenerator
import io
from types import SimpleNamespace

import pandas as pd
from fastapi import Request
from fastapi.responses import StreamingResponse


from mongodb_admin import (
    add_datasets,
    create_users_collection,
    drop_collection,
)
from utils.config import get_config
from utils.error_handler import InternalServerException
from utils.loggr import LOG


async def server_live(request: Request) -> AsyncGenerator:
    """
    Checks the server is live and throws an exception otherwise.

    Args:
        request (Request): Raw request

    Raises:
        InternalServerException: If the server is not live.

    Returns:
        AsyncGenerator
    """
    if not request.app.state.server_state["LIVE"]:
        raise InternalServerException(
            "Woops, the server did not start correctly."
            + "Contact the administrator of this service.",
        )
    yield


def stream_dataframe(df: pd.DataFrame) -> StreamingResponse:
    """
    Creates a streaming response for a given pandas dataframe.

    Args:
        df (pd.DataFrame): The dataframe to stream.

    Returns:
        StreamingResponse: The resulting streaming response.
    """
    stream = io.StringIO()

    # CSV creation
    df.to_csv(stream, index=False)

    response = StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv"
    )
    response.headers["Content-Disposition"] = (
        "attachment; filename=synthetic_data.csv"
    )
    return response


def add_demo_data_to_admindb() -> None:
    """
    Adds the demo data to the mongodb admindb.

    Uses hardcoded paths to user and dataset collections.
    Meant to be used in the develop mode of the service.
    """
    LOG.info("Creating example user collection")

    config = get_config()
    args = SimpleNamespace(**vars(config.admin_database))

    LOG.info("Creating user collection")
    args.clean = True
    args.overwrite = True
    args.path = "/data/collections/user_collection.yaml"
    create_users_collection(args)

    LOG.info("Creating datasets and metadata collection")
    args.path = "/data/collections/dataset_collection.yaml"
    args.overwrite_datasets = True
    args.overwrite_metadata = True
    add_datasets(args)

    LOG.info("Empty archives")
    args.collection = "queries_archives"
    drop_collection(args)
