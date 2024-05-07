from fastapi import Header
from pydantic import BaseModel

from admin_database.admin_database import AdminDatabase
from constants import DPLibraries
from dataset_store.dataset_store import DatasetStore
from dp_queries.dp_querier import DPQuerier
from utils.error_handler import (
    CUSTOM_EXCEPTIONS,
    InternalServerException,
    InvalidQueryException,
    UnauthorizedAccessException,
)


class QueryHandler:
    """
    Query handler for the server.

    Holds a reference to the user database and uses a BasicQuerierManager
    to manage the queriers. TODO make this configurable
    """

    admin_database: AdminDatabase
    dataset_store: DatasetStore

    def __init__(
        self, admin_database: AdminDatabase, dataset_store: DatasetStore
    ) -> None:
        """_summary_

        Args:
            admin_database (AdminDatabase): _description_
            dataset_store (DatasetStore): _description_
        """
        self.admin_database = admin_database
        self.dataset_store = dataset_store

    def _get_querier(
        self,
        query_type: str,
        query_json: BaseModel,
    ) -> DPQuerier:
        """_summary_

        Args:
            query_type (str): _description_
            query_json (BasicModel): _description_

        Raises:
            InternalServerException: _description_
            e: _description_
            InternalServerException: _description_

        Returns:
            DPQuerier: _description_
        """
        # Check query type
        supported_lib = [lib.value for lib in DPLibraries]
        if query_type not in supported_lib:
            raise InternalServerException(
                f"Query type {query_type} not supported in QueryHandler"
            )

        # Get querier
        try:
            dp_querier = self.dataset_store.get_querier(
                query_json.dataset_name, query_type
            )
        except InvalidQueryException as e:
            raise e
        except Exception as e:
            raise InternalServerException(
                "Failed to get querier for dataset "
                + f"{query_json.dataset_name}: {str(e)}"
            ) from e
        return dp_querier

    def estimate_cost(
        self,
        query_type: str,
        query_json: BaseModel,
    ) -> dict[str, float]:
        """_summary_

        Args:
            query_type (str): _description_
            query_json (BasicModel): _description_

        Returns:
            dict[str, float]: _description_
        """
        # Get querier
        dp_querier = self._get_querier(query_type, query_json)

        # Get cost of the query
        eps_cost, delta_cost = dp_querier.cost(query_json)

        return {"epsilon_cost": eps_cost, "delta_cost": delta_cost}

    def handle_query(
        self,
        query_type: str,
        query_json: BaseModel,
        user_name: str = Header(None),
    ) -> dict:
        """_summary_

        Args:
            query_type (str): _description_
            query_json (BasicModel): _description_
            user_name (str, optional): _description_. Defaults to Header(None).

        Raises:
            UnauthorizedAccessException: _description_
            e: _description_
            InvalidQueryException: _description_
            e: _description_
            InternalServerException: _description_
            e: _description_

        Returns:
            dict: _description_
        """
        # Check that user may query
        if not self.admin_database.may_user_query(user_name):
            raise UnauthorizedAccessException(
                f"User {user_name} is trying to query"
                + " before end of previous query."
            )

        # Block access to other queries to user
        self.admin_database.set_may_user_query(user_name, False)

        try:
            # Get querier
            dp_querier = self._get_querier(query_type, query_json)

            # Get cost of the query
            eps_cost, delta_cost = dp_querier.cost(query_json)

            # Check that enough budget to do the query
            try:
                (
                    eps_remain,
                    delta_remain,
                ) = self.admin_database.get_remaining_budget(
                    user_name, query_json.dataset_name
                )
            except UnauthorizedAccessException as e:
                raise e

            if (eps_remain < eps_cost) or (delta_remain < delta_cost):
                raise InvalidQueryException(
                    "Not enough budget for this query epsilon remaining "
                    f"{eps_remain}, delta remaining {delta_remain}."
                )

            # Query
            try:
                query_response = dp_querier.query(query_json)
            except CUSTOM_EXCEPTIONS as e:
                raise e
            except Exception as e:
                raise InternalServerException(e) from e

            # Deduce budget from user
            self.admin_database.update_budget(
                user_name, query_json.dataset_name, eps_cost, delta_cost
            )
            response = {
                "requested_by": user_name,
                "query_response": query_response,
                "spent_epsilon": eps_cost,
                "spent_delta": delta_cost,
            }

            # Add query to db (for archive)
            self.admin_database.save_query(user_name, query_json, response)

        except Exception as e:
            self.admin_database.set_may_user_query(user_name, True)
            raise e

        # Re-enable user to query
        self.admin_database.set_may_user_query(user_name, True)

        # Return response
        return response
