from constants import DPLibraries
from dp_queries.dp_libraries.opendp import OpenDPQuerier
from dp_queries.dp_libraries.smartnoise_sql import SmartnoiseSQLQuerier
from dp_queries.dp_querier import DPQuerier
from private_dataset.private_dataset import PrivateDataset
from utils.error_handler import InternalServerException


def querier_factory(lib: str, private_dataset: PrivateDataset) -> DPQuerier:
    """_summary_

    Args:
        lib (str): _description_
        private_dataset (PrivateDataset): _description_

    Raises:
        InternalServerException: _description_

    Returns:
        DPQuerier: _description_
    """
    match lib:
        case DPLibraries.SMARTNOISE_SQL:
            querier = SmartnoiseSQLQuerier(private_dataset)

        case DPLibraries.OPENDP:
            querier = OpenDPQuerier(private_dataset)

        case _:
            raise InternalServerException(f"Unknown library: {lib}")
    return querier
