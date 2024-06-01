from pydantic import field_validator

__all__ = ["PredefinedStorage", "JsonUserStorage"]


from pydantic import BaseModel, Field, parse_obj_as


class JsonUserStorage(BaseModel):
    class InJsonUser(BaseModel):
        email: str
        groups: list[str] = Field(default_factory=list)

    users: list[InJsonUser] = Field(default_factory=list)

    @field_validator("users")
    def _should_be_unique(cls, v):
        emails = set()
        for user in v:
            if user.email in emails:
                raise ValueError(f"User email {user.email} is not unique")
            emails.add(user.email)
        return v


class PredefinedStorage:
    user_storage: JsonUserStorage

    def __init__(self, user_storage: JsonUserStorage):
        self.user_storage = user_storage

    @classmethod
    def from_jsons(cls, user_json: dict):
        user_storage = parse_obj_as(JsonUserStorage, user_json)
        return cls(user_storage)

    def get_users(self) -> list[JsonUserStorage.InJsonUser]:
        return self.user_storage.users.copy()

    def get_user(self, email: str) -> JsonUserStorage.InJsonUser | None:
        for user in self.user_storage.users:
            if user.email == email:
                return user
        return None
