from fastapi import HTTPException
from starlette import status


class NoCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    responses = {
        401: {"description": "No credentials provided", "headers": {"WWW-Authenticate": {"schema": {"type": "string"}}}}
    }


class IncorrectCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
        )

    responses = {401: {"description": "Could not validate credentials"}}


class ForbiddenException(HTTPException):
    """
    HTTP_403_FORBIDDEN
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=self.responses[403]["description"],
        )

    responses = {403: {"description": "Access denied, not enough permissions"}}


class InvalidReturnToURL(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.responses[400]["description"],
        )

    responses = {400: {"description": "Invalid return_to URL"}}


class ObjectNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or self.responses[404]["description"],
        )

    responses = {404: {"description": "Object not found"}}


class EventGroupNotFoundException(ObjectNotFound):
    responses = {404: {"description": "Event group not found"}}


class EventGroupWithMissingPath(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.responses[400]["description"],
        )

    responses = {400: {"description": "Path is not defined for this event group"}}


class DBException(Exception):
    pass


class DBEventGroupDoesNotExistInDb(DBException):
    def __init__(self, id: int):
        super().__init__(f"Event group with id {id} does not exist in db")
