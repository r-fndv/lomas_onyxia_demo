from abc import ABC, abstractmethod

from admin_database.admin_database import AdminDatabase
from dp_queries.dp_querier import DPQuerier


class DatasetStore(ABC):
    """
    Manages the DPQueriers for the different datasets and libraries

    Holds a reference to the user database in order to get information
    about users.

    We make the _add_dataset function private to enforce lazy loading
    of queriers.
    """

    admin_database: AdminDatabase

    def __init__(self, admin_database: AdminDatabase) -> None:
        self.admin_database = admin_database

    @abstractmethod
    def _add_dataset(self, dataset_name: str) -> None:
        """_summary_

        Args:
            dataset_name (str): _description_
        """

    @abstractmethod
    def get_querier(self, dataset_name: str, library: str) -> DPQuerier:
        """_summary_

        Args:
            dataset_name (str): _description_
            library (str): _description_

        Returns:
            DPQuerier: _description_
        """
