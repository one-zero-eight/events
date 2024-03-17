__all__ = [
    "CURRENT_USER_ID_DEPENDENCY",
    "VERIFY_PARSER_DEPENDENCY",
]

from typing import Annotated
from fastapi import Depends
from src.api.auth.dependencies import get_current_user_id, verify_parser

CURRENT_USER_ID_DEPENDENCY = Annotated[int, Depends(get_current_user_id)]
VERIFY_PARSER_DEPENDENCY = Annotated[bool, Depends(verify_parser)]
