from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import pandas as pd

from lomas_server.utils.collection_models import Metadata


class DataConnector(ABC):
    """
    Overall access to sensitive data
    """

    df: Optional[pd.DataFrame] = None

    def __init__(self, metadata: Metadata) -> None:
        """Initializer.

        Args:
            metadata (Metadata): The metadata for this dataset
        """
        self.metadata: dict = metadata

        dtypes, datetime_columns = get_column_dtypes(metadata)
        self.dtypes: Dict[str, str] = dtypes
        self.datetime_columns: List[str] = datetime_columns

    @abstractmethod
    def get_pandas_df(self, dataset_name: str) -> pd.DataFrame:
        """Get the data in pandas dataframe format

        Args:
            dataset_name (str): name of the private dataset

        Returns:
            pd.DataFrame: The pandas dataframe for this dataset.
        """

    def get_metadata(self) -> dict:
        """Get the metadata for this dataset

        Returns:
            dict: The metadata dictionary.
        """
        return self.metadata


def get_column_dtypes(metadata: dict) -> Tuple[Dict[str, str], List[str]]:
    """Extract and return the column types from the metadata.

    Args:
        metadata (dict): The metadata dictionary.

    Returns:
        dict: The dictionary of the column type.
        list: The list of columns of datetime type
    """
    dtypes = {}
    datetime_columns = []
    for col_name, data in metadata["columns"].items():
        if data["type"] == "datetime":
            dtypes[col_name] = "string"
            datetime_columns.append(col_name)
        else:
            dtypes[col_name] = data["type"]
    return dtypes, datetime_columns
