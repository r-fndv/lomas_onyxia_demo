from typing import List

from pymongo import MongoClient
from pymongo.database import Database

from admin_database.admin_database import (
    AdminDatabase,
    dataset_must_exist,
    user_must_exist,
    user_must_have_access_to_dataset,
)


class AdminMongoDatabase(AdminDatabase):
    """
    Overall MongoDB database management
    """

    def __init__(self, connection_string: str, database_name: str) -> None:
        """Load DB

        Args:
            connection_string (str): Connection string to the mongodb
            database_name (str): Mongodb database name.
        """
        self.db: Database = MongoClient(connection_string)[database_name]

    def does_user_exist(self, user_name: str) -> bool:
        """Checks if user exist in the database

        Args:
            user_name (str): name of the user to check

        Returns:
            bool: _description_
        """
        doc_count = self.db.users.count_documents(
            {"user_name": f"{user_name}"}
        )
        return doc_count > 0

    def does_dataset_exist(self, dataset_name: str) -> bool:
        """Checks if dataset exist in the database

        Args:
            dataset_name (str): name of the dataset to check

        Returns:
            bool: _description_
        """
        collection_query = self.db.datasets.find({})
        for document in collection_query:
            if document["dataset_name"] == dataset_name:
                return True

        return False

    @dataset_must_exist
    def get_dataset_metadata(self, dataset_name: str) -> dict:
        """Returns the metadata dictionnary of the dataset

        Args:
            dataset_name (str): _description_

        Returns:
            dict: _description_
        """
        metadatas = self.db.metadata.find_one(
            {dataset_name: {"$exists": True}}
        )
        return metadatas[dataset_name]  # type: ignore

    @user_must_exist
    def may_user_query(self, user_name: str) -> bool:
        """Checks if a user may query the server.
        Cannot query if already querying.

        Args:
            user_name (str): _description_

        Returns:
            bool: _description_
        """
        user = self.db.users.find_one({"user_name": user_name})
        return user["may_query"]  # type: ignore

    @user_must_exist
    def set_may_user_query(self, user_name: str, may_query: bool) -> None:
        """Sets if a user may query the server.
        (Set False before querying and True after updating budget)

        Args:
            user_name (str): name of the user
            may_query (bool): flag give or remove access to user
        """
        self.db.users.update_one(
            {"user_name": f"{user_name}"},
            {"$set": {"may_query": may_query}},
        )

    @user_must_exist
    def has_user_access_to_dataset(
        self, user_name: str, dataset_name: str
    ) -> bool:
        """Checks if a user may access a particular dataset

        Args:
            user_name (str): name of the user
            dataset_name (str): name of the dataset

        Returns:
            bool: _description_
        """
        doc_count = self.db.users.count_documents(
            {
                "user_name": f"{user_name}",
                "datasets_list.dataset_name": f"{dataset_name}",
            }
        )
        return doc_count > 0

    def get_epsilon_or_delta(
        self, user_name: str, dataset_name: str, parameter: str
    ) -> float:
        """Get the total spent epsilon or delta  by a specific user
        on a specific dataset

        Args:
            user_name (str): name of the user
            dataset_name (str): name of the dataset
            parameter (str): total_spent_epsilon or total_spent_delta

        Returns:
            float: _description_
        """
        return list(
            self.db.users.aggregate(
                [
                    {"$unwind": "$datasets_list"},
                    {
                        "$match": {
                            "user_name": f"{user_name}",
                            "datasets_list.dataset_name": f"{dataset_name}",
                        }
                    },
                ]
            )
        )[0]["datasets_list"][parameter]

    def update_epsilon_or_delta(
        self,
        user_name: str,
        dataset_name: str,
        parameter: str,
        spent_value: float,
    ) -> None:
        """Update the current epsilon spent by a specific user
        with the last spent epsilon

        Args:
            user_name (str): name of the user
            dataset_name (str): name of the dataset
            parameter (str): current_epsilon or current_delta
            spent_value (float): spending of epsilon or delta on last query
        """
        self.db.users.update_one(
            {
                "user_name": f"{user_name}",
                "datasets_list.dataset_name": f"{dataset_name}",
            },
            {"$inc": {f"datasets_list.$.{parameter}": spent_value}},
        )

    @dataset_must_exist
    def get_dataset_field(self, dataset_name: str, key: str) -> str:
        """Get dataset field type based on dataset name and key

        Args:
            dataset_name (str): name of the dataset
            key (str): name of the field to get

        Returns:
            str: _description_
        """
        dataset = self.db.datasets.find_one({"dataset_name": dataset_name})
        return dataset[key]  # type: ignore

    @user_must_have_access_to_dataset
    def get_user_previous_queries(
        self,
        user_name: str,
        dataset_name: str,
    ) -> List[dict]:
        """Retrieves and return the queries already done by a user

        Args:
            user_name (str): name of the user
            dataset_name (str): name of the dataset

        Returns:
            List[dict]: _description_
        """
        queries = self.db.queries_archives.find(
            {
                "user_name": f"{user_name}",
                "dataset_name": f"{dataset_name}",
            },
            {"_id": 0},
        )
        return list(queries)

    def save_query(
        self, user_name: str, query_json: dict, response: dict
    ) -> None:
        """Save queries of user on datasets in a separate collection (table)
        named "queries_archives" in the DB

        Args:
            user_name (str): name of the user
            query_json (dict): json received from client
            response (dict): response sent to the client
        """
        to_archive = super().prepare_save_query(
            user_name, query_json, response
        )
        self.db.queries_archives.insert_one(to_archive)
