from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from constants import INTERNAL_SERVER_ERROR
from utils.loggr import LOG


class InvalidQueryException(Exception):
    """
    Custom exception for invalid queries

    For example, this exception will occur when the query:
        - is not an opendp measurement
        - cannot be reconstructed properly (for opendp and diffprivlib)
    """

    def __init__(self, error_message: str) -> None:
        """_summary_

        Args:
            error_message (str): _description_
        """
        self.error_message = error_message


class ExternalLibraryException(Exception):
    """
    Custom exception for issues within external libraries

    This exception will occur when the processes fail within the
    external libraries (smartnoise-sql, opendp, diffprivlib)
    """

    def __init__(self, library: str, error_message: str) -> None:
        """_summary_

        Args:
            library (str): _description_
            error_message (str): _description_
        """
        self.library = library
        self.error_message = error_message


class UnauthorizedAccessException(Exception):
    """
    Custom exception for unauthorized access:
    (unknown user, no access to dataset, etc)
    """

    def __init__(self, error_message: str) -> None:
        """_summary_

        Args:
            error_message (str): _description_
        """
        self.error_message = error_message


class InternalServerException(Exception):
    """
    Custom exception for issues within server internal functionalities
    like unexpected match cases
    """

    def __init__(self, error_message: str) -> None:
        """_summary_

        Args:
            error_message (str): _description_
        """
        self.error_message = error_message


CUSTOM_EXCEPTIONS: tuple[type, ...] = (
    ExternalLibraryException,
    InternalServerException,
    InvalidQueryException,
    UnauthorizedAccessException,
)


# Custom exception handlers
def add_exception_handlers(app: FastAPI) -> None:
    """_summary_

    Args:
        app (FastAPI): _description_

    Returns:
        _type_: _description_
    """
    @app.exception_handler(InvalidQueryException)
    async def invalid_query_exception_handler(
        _: Request, exc: InvalidQueryException
    ) -> JSONResponse:
        LOG.info(f"InvalidQueryException raised: {exc.error_message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"InvalidQueryException": exc.error_message},
        )

    @app.exception_handler(ExternalLibraryException)
    async def external_library_exception_handler(
        _: Request, exc: ExternalLibraryException
    ) -> JSONResponse:
        LOG.info(f"ExternalLibraryException raised: {exc.error_message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "ExternalLibraryException": exc.error_message,
                "library": exc.library,
            },
        )

    @app.exception_handler(UnauthorizedAccessException)
    async def unauthorized_access_exception_handler(
        _: Request, exc: UnauthorizedAccessException
    ) -> JSONResponse:
        LOG.info(f"UnauthorizedAccessException raised: {exc.error_message}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"UnauthorizedAccessException": exc.error_message},
        )

    @app.exception_handler(InternalServerException)
    async def internal_server_exception_handler(
        _: Request, exc: InternalServerException
    ) -> JSONResponse:
        LOG.info(f"InternalServerException raised: {exc.error_message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"InternalServerException": INTERNAL_SERVER_ERROR},
        )
