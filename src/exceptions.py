from fastapi import HTTPException
from starlette import status


class NoCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )


class IncorrectCredentialsException(HTTPException):
    """
    HTTP_403_FORBIDDEN
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


class InvalidReturnToURL(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid return_to URL",
        )


class UserNotFoundException(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class EventGroupNotFoundException(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event group not found",
        )


class EventGroupWithMissingPath(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is not defined for this event group",
        )


class IcsFileIsNotModified(HTTPException):
    """
    HTTP_304_NOT_MODIFIED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="Event group already connected to the same .ics file",
        )


class OperationIsNotAllowed(HTTPException):
    """
    HTTP_403_FORBIDDEN
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user can not execute this operation",
        )


class DBException(Exception):
    ...


class DBEventGroupDoesNotExistInDb(DBException):
    def __init__(self, id: int):
        super().__init__(f"Event group with id {id} does not exist in db")
