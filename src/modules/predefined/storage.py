__all__ = ["JsonPredefinedUsers"]

from pydantic import BaseModel, Field, TypeAdapter, field_validator


class JsonPredefinedUsers(BaseModel):
    class InJsonUser(BaseModel):
        email: str
        groups: list[str] = Field(default_factory=list)

    users: list[InJsonUser] = Field(default_factory=list)
    academic_groups: dict[str, str] = Field(default_factory=dict)

    @field_validator("users")
    def _should_be_unique(cls, v):
        emails = set()
        for user in v:
            if user.email in emails:
                raise ValueError(f"User email {user.email} is not unique")
            emails.add(user.email)
        return v

    @classmethod
    def from_jsons(cls, user_json: dict):
        type_adapter = TypeAdapter(cls)
        user_storage = type_adapter.validate_python(user_json)
        return user_storage

    def get_users(self) -> list[InJsonUser]:
        return self.users.copy()

    def get_user(self, email: str) -> InJsonUser | None:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def get_academic_group(self, name_in_innohassle_accounts: str) -> str | None:
        return self.academic_groups.get(name_in_innohassle_accounts)
