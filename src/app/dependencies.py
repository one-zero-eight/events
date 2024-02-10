__all__ = [
    "CURRENT_USER_ID_DEPENDENCY",
    "VERIFY_PARSER_DEPENDENCY",
    "Shared",
]

from typing import Annotated, Callable, TypeVar, Union, ClassVar, Hashable

from fastapi import Depends

T = TypeVar("T")

CallableOrValue = Union[Callable[[], T], T]


class Shared:
    """
    Key-value storage with generic type support for accessing shared dependencies
    """

    __slots__ = ()

    providers: ClassVar[dict[type, CallableOrValue]] = {}

    @classmethod
    def register_provider(cls, key: type[T] | Hashable, provider: CallableOrValue):
        cls.providers[key] = provider

    @classmethod
    def f(cls, key: type[T] | Hashable) -> T:
        """
        Get shared dependency by key (f - fetch)
        """
        if key not in cls.providers:
            if isinstance(key, type):
                # try by classname
                key = key.__name__

                if key not in cls.providers:
                    raise KeyError(f"Provider for {key} is not registered")

            elif isinstance(key, str):
                # try by classname
                for cls_key in cls.providers.keys():
                    if cls_key.__name__ == key:
                        key = cls_key
                        break
                else:
                    raise KeyError(f"Provider for {key} is not registered")

        provider = cls.providers[key]

        if callable(provider):
            return provider()
        else:
            return provider


from src.app.auth.dependencies import get_current_user_id, verify_parser  # noqa: E402

CURRENT_USER_ID_DEPENDENCY = Annotated[str, Depends(get_current_user_id)]
VERIFY_PARSER_DEPENDENCY = Annotated[bool, Depends(verify_parser)]
